import 'dart:convert';
import 'dart:io';

Future<void> main() async {
  const url = 'https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json';

  final request = await HttpClient().getUrl(Uri.parse(url));
  final response = await request.close();
  final body = await response.transform(utf8.decoder).join();
  final municipalities = jsonDecode(body) as List<dynamic>;

  print(municipalities.first);
}
