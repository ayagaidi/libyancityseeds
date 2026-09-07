using System.Net.Http;
using System.Text.Json;

record Location(int id, string slug, string name_ar, string name_en, string type);

var url = "https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json";
using var http = new HttpClient();

var json = await http.GetStringAsync(url);
var municipalities = JsonSerializer.Deserialize<List<Location>>(json)
    ?? throw new InvalidOperationException("Invalid dataset response.");

Console.WriteLine(municipalities[0]);
