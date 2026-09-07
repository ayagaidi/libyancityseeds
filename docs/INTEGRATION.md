# Integration Guide

Libya Locations is intentionally **language-agnostic**. You do not need Laravel, PHP, an SDK, an API key, or a package manager.

Any language that can make an HTTP request and parse JSON can use the dataset.

## 30-second integration

Use the stable versioned JSON URL:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json
```

or cities:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/cities.json
```

Each response is a JSON array:

```json
[
  {
    "id": 94,
    "slug": "tripoli-center",
    "name_ar": "طرابلس المركز",
    "name_en": "Tripoli Center",
    "type": "municipality"
  }
]
```

## Stable vs latest URLs

For production applications, pin a release tag:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json
```

For development or previews, use `master`:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/master/data/municipalities.json
```

Pinning a version prevents an upstream dataset update from unexpectedly changing your production application.

## Discover datasets programmatically

Applications that do not want to hard-code individual paths can read:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/endpoints.json
```

It returns the current version, record counts, JSON/CSV URLs, and schema URL.

## Universal data contract

Every location record uses the same fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | integer | Dataset-local stable numeric ID |
| `slug` | string | URL/database-friendly identifier |
| `name_ar` | string | Arabic display name |
| `name_en` | string | English developer-friendly display name |
| `type` | string | `city` or `municipality` |

The machine-readable JSON Schema is available at:

```text
schemas/location.schema.json
```

## cURL

```bash
curl -fsSL \
  https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json
```

Download for local/offline use:

```bash
curl -fsSL \
  https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json \
  -o municipalities.json
```

## JavaScript / TypeScript

```js
const url = 'https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json';
const locations = await fetch(url).then(response => response.json());
```

## Python

```python
import json
from urllib.request import urlopen

url = "https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json"
with urlopen(url) as response:
    locations = json.load(response)
```

## PHP

```php
$url = 'https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json';
$locations = json_decode(file_get_contents($url), true, flags: JSON_THROW_ON_ERROR);
```

## Go

```go
resp, err := http.Get(url)
if err != nil { log.Fatal(err) }
defer resp.Body.Close()

var locations []Location
if err := json.NewDecoder(resp.Body).Decode(&locations); err != nil {
    log.Fatal(err)
}
```

## C# / .NET

```csharp
using var http = new HttpClient();
var json = await http.GetStringAsync(url);
var locations = JsonSerializer.Deserialize<List<Location>>(json);
```

## Dart / Flutter

```dart
final request = await HttpClient().getUrl(Uri.parse(url));
final response = await request.close();
final body = await response.transform(utf8.decoder).join();
final locations = jsonDecode(body) as List<dynamic>;
```

## Swift

```swift
let (data, _) = try await URLSession.shared.data(from: URL(string: url)!)
let locations = try JSONDecoder().decode([Location].self, from: data)
```

## Java

Java 11+ can fetch the JSON with the built-in HTTP client. Parse the response with the JSON library already used by your application (Jackson, Gson, JSON-B, etc.).

```java
var client = HttpClient.newHttpClient();
var request = HttpRequest.newBuilder(URI.create(url)).GET().build();
var response = client.send(request, HttpResponse.BodyHandlers.ofString());
String json = response.body();
```

## Ruby

```ruby
require 'json'
require 'open-uri'

locations = JSON.parse(URI.open(url).read)
```

## Mobile, backend, frontend, and offline apps

You can choose either integration model:

1. **Remote:** fetch the versioned JSON file when your app needs it and cache it locally.
2. **Bundled:** download the JSON/CSV file during build/deployment and ship it with your application.
3. **Database import:** transform the JSON/CSV into your own database schema.

The data format does not require a specific framework or database.

## Recommended production pattern

- Pin a release such as `v1.1.0`.
- Cache the response instead of downloading it on every request.
- Use `slug` as the integration identifier when possible.
- Store your own foreign key if importing into a database.
- Upgrade dataset versions intentionally after reviewing the changelog.

## More examples

See [`examples/README.md`](../examples/README.md) for copy-paste examples in common languages.
