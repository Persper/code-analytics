require 'rugged'
require 'linguist'
require 'json'

repo_path = ARGV[0]
repo = Rugged::Repository.new(repo_path)

project = Linguist::Repository.new(repo, repo.head.target_id)
puts JSON.pretty_generate(project.languages)
