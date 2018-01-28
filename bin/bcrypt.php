#!/usr/bin/env php
<?php # Захэшировать пароль в bcrypt
printf("hash for \"%s\": %s \n", $argv[1], password_hash($argv[1], PASSWORD_BCRYPT));
