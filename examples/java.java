import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class LibyaLocationsExample {
    public static void main(String[] args) throws Exception {
        var url = "https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json";
        var client = HttpClient.newHttpClient();
        var request = HttpRequest.newBuilder(URI.create(url)).GET().build();
        var response = client.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() >= 400) {
            throw new IllegalStateException("HTTP " + response.statusCode());
        }

        // Parse response.body() with the JSON library your app already uses
        // (Jackson, Gson, JSON-B, etc.).
        System.out.println(response.body().substring(0, Math.min(200, response.body().length())));
    }
}
