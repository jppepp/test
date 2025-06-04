using InflationComparison.Models;

namespace InflationComparison.Services
{
    public interface IDataService
    {
        Task<IEnumerable<InflationData>> GetComparisonDataAsync(string country1, string country2);
        Task<int> GetInflationCalculateResult(string country, int startYear, int endYear);
        Task<IEnumerable<InflationData>> GetCategoryComparisonAsync(string country1, string country2, string category);
        Task<IEnumerable<Country>> GetCountriesAsync();
        Task<IEnumerable<DataType>> GetDataTypesAsync();
        Task<IEnumerable<News>> GetLatestNewsAsync(int limit = 10);
        Task<IEnumerable<News>> GetNewsBySourceAsync(string source, int limit = 3);
        Task<IEnumerable<string>> GetAllNewsSourcesAsync();
        Task<IEnumerable<InflationData>> GetSpecificCategoryDataAsync(string country1, string country2, string category);
    }
}