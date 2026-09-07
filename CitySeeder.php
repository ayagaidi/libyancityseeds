<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use RuntimeException;

/**
 * Backward-compatible seeder for users of the repository's original file.
 *
 * New projects should prefer database/seeders/LibyaCitySeeder.php.
 */
class CitySeeder extends Seeder
{
    public function run(): void
    {
        $path = base_path('data/cities.json');

        if (! is_file($path)) {
            throw new RuntimeException("Libya city dataset not found at {$path}");
        }

        $rows = json_decode(file_get_contents($path), true, flags: JSON_THROW_ON_ERROR);
        $now = now();

        $payload = array_map(static fn (array $row): array => [
            'slug' => $row['slug'],
            'name_ar' => $row['name_ar'],
            'name_en' => $row['name_en'],
            'created_at' => $now,
            'updated_at' => $now,
        ], $rows);

        DB::table('cities')->upsert(
            $payload,
            ['slug'],
            ['name_ar', 'name_en', 'updated_at'],
        );
    }
}
