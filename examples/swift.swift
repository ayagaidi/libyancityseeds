import Foundation

struct Location: Decodable {
    let id: Int
    let slug: String
    let name_ar: String
    let name_en: String
    let type: String
}

let url = URL(string: "https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json")!
let (data, _) = try await URLSession.shared.data(from: url)
let municipalities = try JSONDecoder().decode([Location].self, from: data)

print(municipalities[0])
