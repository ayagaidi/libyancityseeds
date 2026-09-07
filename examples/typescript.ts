type LibyaLocation = {
  id: number;
  slug: string;
  name_ar: string;
  name_en: string;
  type: 'city' | 'municipality';
};

const url = 'https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json';

const response = await fetch(url);
if (!response.ok) throw new Error(`HTTP ${response.status}`);

const municipalities = (await response.json()) as LibyaLocation[];
console.log(municipalities[0]);
