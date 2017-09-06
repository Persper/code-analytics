# coding: utf-8
import array
import numpy as np
import sklearn
import sklearn.ensemble
import sklearn.metrics
from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin, clone, is_classifier
from sklearn.preprocessing import StandardScaler, label_binarize, binarize, normalize, LabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline, make_union
import functools
from scipy.stats import norm
from scipy.sparse import csr_matrix, csc_matrix
from joblib import Parallel, delayed
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score, confusion_matrix, classification_report

# Stemmer language processing - http://qinxuye.me/article/porter-stemmer/
import nltk
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

def stem(text):
    stemmed = []
    tokens = nltk.word_tokenize(text)
    for token in tokens:
        stemmed.append(stemmer.stem(token))
    return stemmed

# Spacy language processing - https://spacy.io/
import spacy
nlp = spacy.load('en')

def lemmatize(text):
    lemmatized = []
    doc = nlp(text)
    for token in doc:
        if token.pos_ != 'PUNCT':
            lemmatized.append(token.lemma_)
    return lemmatized

# The random forest classifier
import functools
rf = functools.partial(sklearn.ensemble.RandomForestClassifier, n_estimators=300)

# import the labeler lib 0 
import sys
sys.path.append('../lib')
from labeler import apache_labeler
from labeler import fs_labeler

# issue/patch type classification
def binary_bug(issue, is_jira):
    if is_jira:
        if issue['type'] == 'Bug':
            return 1
        else:
            return 0
    else:
        if issue['type'] == 'b':
            return 1
        else:
            return 0

def multi_patch_type(issue, is_jira):
    return issue['type']

def limited_patch_type(issue, is_jira):
    if is_jira:
        return apache_labeler[issue['type']]
    else:
        return fs_labeler[issue['cons_type']]

def only_bug_filter(issue, is_jira):
    if is_jira:
        return issue['type'] == 'Bug'
    else:
        return issue['type'] == 'b'
    
# BNS
def bns(tprs, fprs):
    """
    Args:
        tprs: A row vector of shape (1, num_features)
        fprs: A row vector of shape (1, num_features)
    """
    num_features = tprs.shape[1]
    bns = np.zeros(num_features)
    for i in range(num_features):
        bns[i] = np.abs(norm.ppf(tprs[0, i]) - norm.ppf(fprs[0, i]))
    return bns

def tfbns(tfs, bns):
    """
    Args:
        tfs: A sparse matrix of shape (num_samples, num_features)
            in csr format
        bns: A numpy array of shape (num_features,)
    """
    cx = tfs.tocoo()
    data, rows, cols = [], [], []
    for i, j, v in zip(cx.row, cx.col, cx.data):
        data.append(v * bns[j])
        rows.append(i)
        cols.append(j)
    return csr_matrix((data, (rows, cols)), shape=tfs.shape)

# Text Preprocessing using tfidf or bns
class TextTransformer(BaseEstimator, TransformerMixin):
    
    def __init__(self, use_bns):
        self.use_bns = use_bns
        if self.use_bns:
            self.tf_trans = TfidfTransformer(use_idf=False, norm=None)
        else:
            self.tf_trans = TfidfTransformer()
        
    def fit(self, X, y=None):
        self.tf_trans.fit(X)
        
        if self.use_bns:
            binary_counts = binarize(X)

            pos = np.sum(y)
            neg = np.size(y) - pos
            
            tps = np.sum(binary_counts[np.nonzero(y)[0]], axis=0)
            
            fps = np.sum(binary_counts[np.argwhere(y == 0)[:, 0]], axis=0)

            tprs = np.clip(tps / pos, 0.0005, 0.9995)
            fprs = np.clip(fps / neg, 0.0005, 0.9995)

            self.bns_values = bns(tprs, fprs)
            
        return self
        
    def transform(self, counts):
        tfs = self.tf_trans.transform(counts)
        if self.use_bns:
            return normalize(tfbns(tfs, self.bns_values))
        else:
            return tfs
        
# Extract the title/descrption/comments/priority/type for jira issues and 'text'/'frc' for fs patches
class FeatureLabelExtractor(BaseEstimator, TransformerMixin):
    """Cannot be used in Pipeline"""
    
    def __init__(self, datasets, text_feature, label_func, file_filter, is_jira):
        self.datasets = datasets
        self.text_feature = text_feature
        self.label_func = label_func
        self.file_filter = file_filter
        self.is_jira = is_jira
    
    def fit(self, X, y=None):
        return self
    
    def jira_issue_transform(self, project_list, use_description, use_comment):
        num_samples = sum([
            sum([1 for issue in self.datasets[fs] if self.file_filter(issue)]) 
            for fs in project_list])
        
        features = {}
        features['text'] = [None] * num_samples
        labels = [None] * num_samples
        ind = 0
        for project in project_list:
            for issue_id, issue in self.datasets[project].items():
                if self.file_filter(issue):
                    features['text'][ind] = issue[self.text_feature]
                    if use_description and  'description' not in self.text_feature:
                        features['text'][ind] = issue[self.text_feature] + issue['description'].strip()
                    if use_comment and 'comment' not in self.text_feature:
                        features['text'][ind] = issue[self.text_feature] + issue['comment'].strip()
                    if use_description and use_comment:
                        features['text'][ind] = issue[self.text_feature] + issue['description'].strip() + issue['comment'].strip()
                    labels[ind] = self.label_func(issue, self.is_jira)
                    ind += 1
        return features, labels

    def fs_patch_transform(self, fs_list):
        num_samples = sum([
            sum([1 for dp in self.datasets[fs] if self.file_filter(dp)]) 
            for fs in fs_list])
        
        features = {}
        features['text'] = [None] * num_samples
        features['frc'] = np.zeros((num_samples, 3))
        labels = [None] * num_samples
        ind = 0
        for fs in fs_list:
            for dp in self.datasets[fs]:
                if self.file_filter(dp):
                    features['text'][ind] = dp[self.text_feature]
                    features['frc'][ind] = np.array([dp['num_files'],
                                          dp['num_adds'],
                                          dp['num_dels']])
                    labels[ind] = self.label_func(dp, self.is_jira)
                    ind += 1
        return features, labels
    
class ItemSelector(BaseEstimator, TransformerMixin):
    
    def __init__(self, key):
        self.key = key
        
    def fit(self, x, y=None):
        return self
    
    def transform(self, data_dict):
        return data_dict[self.key]

def _fit_binary(estimator, use_bns, use_text, use_frc, k, X, y):
    estimator = clone(estimator)
    text = make_pipeline(
        ItemSelector(key='count'), TextTransformer(use_bns=use_bns))
    frc = make_pipeline(
        ItemSelector(key='frc'), StandardScaler())
        
    if use_text and use_frc:
        union = make_union(text, frc)
    elif not use_text and use_frc:
        union = frc
    elif use_text and not use_frc:
        union = text
        
    if k:
        pipeline = make_pipeline(union, SelectKBest(mutual_info_classif, k=k), estimator)
    else:
        pipeline = make_pipeline(union, estimator)
    
    pipeline.fit(X, y)
    return pipeline 

def _predict_binary(pipeline, X):
    """Make predictions using a single binary estimator"""
    try:
        score = np.ravel(pipeline.decision_function(X))
    except (AttributeError, NotImplementedError):
        score = pipeline.predict_proba(X)[:, 1]
    return score
    

class BNSClassifier(BaseEstimator, ClassifierMixin):
    
    def __init__(self, estimator, use_bns, 
                 use_text, use_frc, k, n_jobs=1):
        assert(use_text or use_frc)
        self.estimator = estimator
        self.n_jobs = n_jobs
        self.use_bns = use_bns
        self.use_text = use_text
        self.use_frc = use_frc
        self.k = k
        
    def fit(self, X, y):
        self.label_binarizer = LabelBinarizer(sparse_output=True)
        Y = self.label_binarizer.fit_transform(y)
        Y = Y.tocsc()
        self.classes = self.label_binarizer.classes_
        columns = (col.toarray().ravel() for col in Y.T)
        
        self.pipelines = Parallel(n_jobs=self.n_jobs)(
            delayed(_fit_binary)(
                self.estimator, self.use_bns, 
                self.use_text, self.use_frc, self.k, X, column)
            for column in columns)
        
    def predict(self, X):
        if(hasattr(self.pipelines[0], 'decision_function') and
              is_classifier(self.pipelines[0])):
            thresh = 0
        else:
            thresh = 0.5
            
        n_samples = X['count'].shape[0]
        if self.label_binarizer.y_type_ == 'multiclass':
            maxima = np.empty(n_samples, dtype=float)
            maxima.fill(-np.inf)
            argmaxima = np.zeros(n_samples, dtype=int)
            for i, p in enumerate(self.pipelines):
                pred = _predict_binary(p, X)
                np.maximum(maxima, pred, out=maxima)
                argmaxima[maxima == pred] = i
            return self.classes[np.array(argmaxima.T)]
        else:
            indices = array.array('i')
            indptr = array.array('i', [0])
            for p in self.pipelines:
                indices.extend(np.where(_predict_binary(p, X) > thresh)[0])
                indptr.append(len(indices))
            data = np.ones(len(indices), dtype=int)
            indicator = csc_matrix((data, indices, indptr),
                shape=(n_samples, len(self.pipelines)))
            return self.label_binarizer.inverse_transform(indicator)

class Classifier():
    
    def __init__(self, datasets, file_list):
        """
        Args:
            datasets: A dictionary, keys are dataset names, each dataset
                is a list of data points (also dictionaries).
            file_list: A list of jira issue names.
        """
        self.datasets = datasets
        self.file_list = file_list

    def _clean(self):
        self.feature_labels = {}
        self.classifiers = {}

    def run(self, label_func, estimator, ngram_range=(1, 1),
            text_feature='', use_text=True, use_frc=False,
            dp_filter=lambda dp: True, tokenizer=None, 
            max_features=None, min_df=1, use_bns=False, k=None,
            n_jobs=1, use_description=False, use_comment=False, 
            use_svm=False, svm_type='linear', 
            use_rf=False, num_estimators = 100, val_max_features=0.5, 
             is_jira=False):
        """Perform experiment in a leave-one-out style
        
        Args:
            label_func: A function, takes a data point as input and
                return its target label.
            estimator: A function, return a classifier which supports
                'fit' and 'predict' method
            ngram_range: A tuple of two integers, specify what range of 
                ngram to use
            text_feature: A string, 
                can be either 'title' or 'description' or 'comment' for jira issue, 
                and can be either 'message' or 'subject' for fs patch.
                If set to None, then texts will not be used.
            use_text: A boolean flag, whether to use text feature
            use_frc: A boolean flag, whether to use frc
            dp_filter: A function decides which data point to exclude.
            tokenizer: A function takes a string and return a list of tokens.
            max_features: An int or None. If not None, only consider
                top max_features ordered by term frequency across the corpus.
            min_df: An int, ignore terms when building vocabulary if their
                document frequency is strictly lower than this threshold.
            use_bns: A boolean flag, use BNS if True, otherwise use IDF
            k: An int, number of top features to keep during feature selection. 
        """
        self._clean()
        
        if text_feature == '': 
            if is_jira:
                text_feature = 'title'
            else:
                text_feature = 'message'
        
        iss = FeatureLabelExtractor(self.datasets, text_feature, label_func, dp_filter, is_jira)
        
        for jr in self.file_list:
            ofs_list = [ojr for ojr in self.file_list if ojr != jr]

            if is_jira:
                train_X, train_y = iss.jira_issue_transform(ofs_list, use_description, use_comment)
                test_X, test_y = iss.jira_issue_transform([jr], use_description, use_comment)
            else:
                train_X, train_y = iss.fs_patch_transform(ofs_list)
                test_X, test_y = iss.fs_patch_transform([jr])

            cv = CountVectorizer(tokenizer=tokenizer,
                                 ngram_range=ngram_range,
                                 max_features=max_features,
                                 min_df=min_df)
            
            train_X['count'] = cv.fit_transform(train_X['text'])
            test_X['count'] = cv.transform(test_X['text'])

            # TODO set n_jobs
            if use_svm:
                clf = BNSClassifier(estimator(kernel=svm_type), 
                                use_bns=use_bns,
                                use_text=use_text,
                                use_frc=use_frc,
                                k=k,
                                n_jobs=n_jobs)
            elif use_rf:
                clf = BNSClassifier(estimator(n_estimators = num_estimators, max_features=val_max_features), 
                                use_bns=use_bns,
                                use_text=use_text,
                                use_frc=use_frc,
                                k=k,
                                n_jobs=n_jobs)
            else:
                clf = BNSClassifier(estimator(), 
                                use_bns=use_bns,
                                use_text=use_text,
                                use_frc=use_frc,
                                k=k,
                                n_jobs=n_jobs)
            clf.fit(train_X, train_y)

            print('----------  Test Accuracy for %s ---------- ' % jr)
            #print('Classifier: %.3f' % clf.score(test_X, test_y))
            predictions=clf.predict(test_X)
            print ('Accuracy: %.3f.' % accuracy_score(test_y,predictions))
            print ('precision/recall/f1-score:')
            print (classification_report(test_y,predictions))
            print ('confusion_matrix:')
            print (confusion_matrix(test_y,predictions))
            print ()
            
            self.classifiers[jr] = clf
