var router = require('express').Router();
var bodyParser = require('body-parser');
var passport = require('passport');
var _ = require('lodash');
var HmacStrategy = require('passport-hmac');
const { reportMetrics } = require('./dataSources');
const logger = require('./logger');

const apps = [
  {
    appName: 'fox.one',
    accessKey: 'f54BK6vJHmDLBhcft5QMsInsoI9igc4E',
    secretKey: 'Dvg0DrOuSrmgqVWpFGfaPHS8rwdxzOFMkQ10576hsgfpQqqF39VCeTlU7irngnJH',
  },
  {
    appName: 'test',
    accessKey: '25goUUxjVMGZrqLxDuA349wZ8aRkLg1z',
    secretKey: '9LyhcQyU8quQrUudypTyWIkTOuQld6ezj14j5aw0U759bRQRLlLbLgPOt93LrMqU',
  }
]

passport.use(new HmacStrategy(
  function(publicKey, done) {
    let app = _.find(apps, { accessKey: publicKey });
    if (!app) { return done(null, false); }
    let { secretKey: privateKey } = app;
    return done(null, app, privateKey);
  }
));

// Initialize Passport
// router.use(passport.initialize());

router.use(bodyParser.json())

router.get('/project/metrics',
  function(req, res, next) {
    passport.authenticate('hmac', function(err, user, info) {

        // When verify hmac happend error
        if (err) {
          res.status(500);
          res.end('Authenticate error');
          logger.error(err);
          return;
        }

        // Client hmac invalid
        if (!user) {
            res.status(401);
            res.end(info.message);
            return;
        }

        // Get data from request
        let { git_urls = '' } = req.query;
        let gitUrls = _.map(git_urls.split(','), decodeURIComponent);

        // Verify the git urls data
        let invalidGitUrls = _.filter(gitUrls,(item) => !item || !new RegExp('((git|ssh|http(s){0,1})|(git@[\\w\\.]{1,}))(:(//){0,1})([\\w\\.@:/\\-~]{1,})(/){0,1}', 'g').test(item));
        if(invalidGitUrls.length > 0){
          res.json({
            code: 'INVALID_GIT_URL',
            message: 'Git url invalid.',
            data: {
              invalid_git_urls: invalidGitUrls,
            }
          });
          return;
        }

        //GRPC call
        reportMetrics.GetMetrics({
          git_url_list: gitUrls,
        },(err, response)=>{
          // When call grpc return an error
          if(err){
            res.status(500);
            res.end('Call error');
            logger.error(err);
            return;
          }

          // Parse response data
          let { status, metrics_list } = response;

          // Response data to client
          if(status.code === 'SUCCESS'){
            res.json({
              code: 'SUCCESS',
              message: 'OK',
              data: {
                project_list: metrics_list
              }
            });
          }else{
            res.status(500);
            res.end('Response error');
            logger.error(new Error(status));
            return;
          }
        });

    })(req, res, next);
  }
);

module.exports = router;
