#!/bin/bash

N=100
M=1000

../stats_pr.py -n $N -d ../repos/hbase -t rel/1.3.0 -k HBASE -m $M > hbase.pr.csv &
../stats_pr.py -n $N -d ../repos/spark -t v2.1.0 -k SPARK -m $M > spark.pr.csv &
../stats_pr.py -n $N -d ../repos/zookeeper -t release-3.4.9 -k ZOOKEEPER	-m $M > zookeeper.pr.csv &
../stats_pr.py -n $N -d ../repos/incubator-systemml -t v0.14.0-incubating-rc4 -k SYSTEMML -m $M > systemml.pr.csv &
../stats_pr.py -n $N -d ../repos/maven -t maven-3.3.9 -k MNG -m $M > maven.pr.csv &
../stats_pr.py -n $N -d ../repos/cassandra -t cassandra-3.10 -k CASSANDRA -m $M > cassandra.pr.csv &
../stats_pr.py -n $N -d ../repos/couchdb -t 2.0.0 -k COUCHDB -m $M > couchdb.pr.csv &
../stats_pr.py -n $N -d ../repos/hive -t rel/release-2.1.1 -k HIVE -m $M > hive.pr.csv &
../stats_pr.py -n $N -d ../repos/rails -t v5.1.1 -m $M > rails.pr.csv &
../stats_pr.py -n $N -d ../repos/opencv -t 3.2.0 -m $M > opencv.pr.csv & 
../stats_pr.py -n $N -d ../repos/tensorflow -t v1.1.0 -m $M > tensorflow.pr.csv &
../stats_pr.py -n $N -d ../repos/vagrant -t v1.9.4 -m $M > vagrant.pr.csv &
../stats_pr.py -n $N -d ../repos/jekyll -t v3.4.3 -m $M > jekyll.pr.csv &
../stats_pr.py -n $N -d ../repos/discourse -t v1.7.8 -m $M > discourse.pr.csv &

for pid in $(jobs -p)
do
  wait $pid
done

