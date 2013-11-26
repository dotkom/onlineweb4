#!/bin/bash

echo "----------------------------------"
echo "- Deleting merged local branches -"
echo "----------------------------------"
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d

echo "------------------------------------"
echo "- Pruning origin's merged branches -"
echo "------------------------------------"
git remote update --prune

