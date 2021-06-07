#!/usr/bin/env php
<?php
//---
//title: Захэшировать пароль в bcrypt
//tags: []
//refs: []
//---
printf("hash for \"%s\": %s \n", $argv[1], password_hash($argv[1], PASSWORD_BCRYPT));
