<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Route;

// Example routes for routes/api.php.
// These examples assume the migrations and seeders from this repository were copied into your app.

Route::get('/libya/municipalities', function (Request $request) {
    $locale = $request->string('lang')->lower()->value() === 'ar' ? 'ar' : 'en';
    $nameColumn = $locale === 'ar' ? 'name_ar' : 'name_en';

    return DB::table('municipalities')
        ->orderBy($nameColumn)
        ->get(['id', 'slug', $nameColumn])
        ->map(fn ($row) => [
            'id' => $row->id,
            'slug' => $row->slug,
            'name' => $row->{$nameColumn},
        ]);
});

Route::get('/libya/cities', function (Request $request) {
    $locale = $request->string('lang')->lower()->value() === 'ar' ? 'ar' : 'en';
    $nameColumn = $locale === 'ar' ? 'name_ar' : 'name_en';

    return DB::table('cities')
        ->orderBy($nameColumn)
        ->get(['id', 'slug', $nameColumn])
        ->map(fn ($row) => [
            'id' => $row->id,
            'slug' => $row->slug,
            'name' => $row->{$nameColumn},
        ]);
});
