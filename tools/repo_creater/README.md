# Repo Creater Tool

**Goal**: To be able to quickly create fake development history for test purpose 
    
# Workflow
1. `cd test`  and `mkdir <name_of_this_test>`
2. For each commit in the fake history, `mkdir <commit_dir>`
3. Add source files for each commit
4. Write commit graph to `cg.dot` file, see `test/test_feature_branch/cg.dot` for an example. You can also plot it out for inspection with `dot -Tpng cg.dot -o cg.png`
5. Run repo_creater tool
```
cd tools/repo_creater
./create_repo.py ../../test/<name_of_this_test>
```
The newly created repo has the same name and will be under `repos/` folder.

6. Examine repo history
```	
cd repos/<name_of_this_test>
git log --graph
# alternatively, to see only master
git log --first-parent
```

# Assumptions
- Merge only happens on master branch
- No merge conflicts resolved manually.
- All files dwell directly under `<commit_dir>`  (not in some subfolders)

