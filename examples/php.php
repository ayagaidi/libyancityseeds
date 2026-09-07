<?php

$url = 'https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json';
$json = file_get_contents($url);

if ($json === false) {
    throw new RuntimeException('Unable to download Libya locations dataset.');
}

$municipalities = json_decode($json, true, flags: JSON_THROW_ON_ERROR);

print_r($municipalities[0]);
