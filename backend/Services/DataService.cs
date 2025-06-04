using Dapper;
using InflationComparison.Models;
using Npgsql;

namespace InflationComparison.Services
{
    public class DataService : IDataService
    {
        private readonly string _connectionString;

        public DataService(string connectionString)
        {
            _connectionString = connectionString;
        }

        public async Task<IEnumerable<InflationData>> GetComparisonDataAsync(string country1, string country2)
        {
            const string query = @"
                SELECT 
                    i.year AS Year, 
                    i.rate AS Rate, 
                    c.name AS Country, 
                    dt.type_name AS DataType,
                    i.source AS Source
                FROM inflation_rates i
                JOIN countries c ON i.country_id = c.id
                JOIN data_types dt ON i.data_type_id = dt.id
                WHERE c.name IN (@Country1, @Country2)
                AND dt.is_official = true
                AND i.year >= EXTRACT(YEAR FROM CURRENT_DATE) - 10
                ORDER BY i.year, c.name";

            using (var connection = new NpgsqlConnection(_connectionString))
            {
                return await connection.QueryAsync<InflationData>(query, new
                {
                    Country1 = country1,
                    Country2 = country2,
                });
            }
        }

        public async Task<IEnumerable<InflationData>> GetCategoryComparisonAsync(string country1, string country2, string category)
        {
            var query = @"
        SELECT 
            i.year AS Year, 
            i.rate AS Rate, 
            c.name AS Country, 
            dt.type_name AS DataType,
            i.source AS Source
        FROM inflation_rates i
        JOIN countries c ON i.country_id = c.id
        JOIN data_types dt ON i.data_type_id = dt.id
        WHERE c.name IN (@Country1, @Country2)
        AND dt.type_name = @Category";

            // Для всех категорий кроме общей инфляции берем только последние данные
            if (category != "CPI Inflation")
            {
                query += @" AND i.year = (
            SELECT MAX(year) 
            FROM inflation_rates 
            WHERE country_id = i.country_id 
            AND data_type_id = i.data_type_id
        )";
            }
            else
            {
                query += " AND i.year >= EXTRACT(YEAR FROM CURRENT_DATE) - 10";
            }

            query += " ORDER BY i.year, c.name";

            using (var connection = new NpgsqlConnection(_connectionString))
            {
                var results = await connection.QueryAsync<InflationData>(query, new
                {
                    Country1 = country1,
                    Country2 = country2,
                    Category = category
                });

                return results.Select(r =>
                {
                    if (double.IsNaN(r.Rate ?? 0)) r.Rate = null;
                    return r;
                });
            }
        }

        public async Task<IEnumerable<InflationData>> GetSpecificCategoryDataAsync(string country1, string country2, string category)
        {
            const string query = @"
        SELECT 
            i.year AS Year, 
            i.rate AS Rate, 
            c.name AS Country, 
            dt.type_name AS DataType,
            i.source AS Source
        FROM inflation_rates i
        JOIN countries c ON i.country_id = c.id
        JOIN data_types dt ON i.data_type_id = dt.id
        WHERE c.name IN (@Country1, @Country2)
        AND dt.type_name = @Category
        AND i.year = (SELECT MAX(year) FROM inflation_rates 
                     WHERE country_id = i.country_id AND data_type_id = i.data_type_id)
        ORDER BY c.name";

            using (var connection = new NpgsqlConnection(_connectionString))
            {
                return await connection.QueryAsync<InflationData>(query, new
                {
                    Country1 = country1,
                    Country2 = country2,
                    Category = category
                });
            }
        }

        public async Task<IEnumerable<Country>> GetCountriesAsync()
        {
            const string query = "SELECT id, name FROM countries ORDER BY name";

            using (var connection = new NpgsqlConnection(_connectionString))
            {
                return await connection.QueryAsync<Country>(query);
            }
        }

        public async Task<IEnumerable<DataType>> GetDataTypesAsync()
        {
            const string query = "SELECT id, type_name AS TypeName, is_official AS IsOfficial FROM data_types ORDER BY type_name";

            using (var connection = new NpgsqlConnection(_connectionString))
            {
                return await connection.QueryAsync<DataType>(query);
            }
        }

        public async Task<IEnumerable<News>> GetLatestNewsAsync(int limit = 10)
        {
            const string query = @"
                SELECT 
                    id AS Id,
                    title AS Title,
                    date AS Date,
                    link AS Link,
                    source AS Source,
                    created_at AS CreatedAt
                FROM news 
                ORDER BY created_at DESC 
                LIMIT @Limit";

            using (var connection = new NpgsqlConnection(_connectionString))
            {
                return await connection.QueryAsync<News>(query, new { Limit = limit });
            }
        }

        // Добавляем новые методы в DataService
        public async Task<IEnumerable<News>> GetNewsBySourceAsync(string source, int limit = 3)
        {
            string query = @"
        SELECT 
            id AS Id,
            title AS Title,
            date AS Date,
            link AS Link,
            source AS Source,
            created_at AS CreatedAt
        FROM news
        WHERE source = @Source
        ORDER BY created_at DESC
        LIMIT @Limit";

            using (var connection = new NpgsqlConnection(_connectionString))
            {
                return await connection.QueryAsync<News>(query, new
                {
                    Source = source,
                    Limit = limit
                });
            }
        }

        public async Task<IEnumerable<string>> GetAllNewsSourcesAsync()
        {
            const string query = "SELECT DISTINCT source FROM news ORDER BY source";

            using (var connection = new NpgsqlConnection(_connectionString))
            {
                return await connection.QueryAsync<string>(query);
            }
        }

        public async Task<IEnumerable<News>> GetFilteredNewsAsync(string country, string year, int limit = 10)
        {
            const string query = @"
                SELECT 
                    id AS Id,
                    title AS Title,
                    date AS Date,
                    link AS Link,
                    source AS Source,
                    created_at AS CreatedAt
                FROM news
                WHERE country = @Country AND EXTRACT(YEAR FROM date) = @Year::int
                ORDER BY created_at DESC
                LIMIT @Limit";

            using (var connection = new NpgsqlConnection(_connectionString))
            {
                return await connection.QueryAsync<News>(query, new
                {
                    Country = country,
                    Year = year,
                    Limit = limit
                });
            }
        }

        public async Task<int> GetInflationCalculateResult(string country, int startYear, int endYear)
        {
            const string query = @"
                SELECT 
                    rate as Rate
                FROM inflation_rates i
                JOIN countries c on i.country_id = c.id
                WHERE c.name = @country AND i.year BETWEEN @startYear AND @endYear";

            using var connection = new NpgsqlConnection(_connectionString);
            var rates = await connection.QueryAsync<int>(query, new
            {
                country,
                startYear,
                endYear
            });

            return (int)rates.Average();
        }
    }
}