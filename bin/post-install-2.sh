#!/bin/sh

rm -rf ./group_vars/development/ &&
cd ./../site &&
php console key:generate &&
cd ./../trellis &&
echo 'Done'
