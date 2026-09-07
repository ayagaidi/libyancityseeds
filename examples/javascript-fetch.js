const MUNICIPALITIES_URL =
  'https://raw.githubusercontent.com/ayagaidi/libyancityseeds/master/data/municipalities.json';

async function loadLibyaMunicipalities(locale = 'en') {
  const response = await fetch(MUNICIPALITIES_URL);

  if (!response.ok) {
    throw new Error(`Failed to load municipalities: ${response.status}`);
  }

  const municipalities = await response.json();
  const nameKey = locale === 'ar' ? 'name_ar' : 'name_en';

  return municipalities.map(({ id, slug, [nameKey]: name }) => ({
    id,
    slug,
    name,
  }));
}

loadLibyaMunicipalities('ar').then(console.table);
