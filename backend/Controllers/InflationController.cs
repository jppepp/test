using InflationComparison.Models;
using InflationComparison.Services;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/[controller]")]
public class InflationController : ControllerBase
{
    private readonly IDataService _dataService;

    public InflationController(IDataService dataService)
    {
        _dataService = dataService;
    }

    [HttpGet("compare")]
    public async Task<ActionResult<IEnumerable<InflationData>>> CompareCountries(
        [FromQuery] string country1,
        [FromQuery] string country2)
    {
        if (string.IsNullOrEmpty(country1) || string.IsNullOrEmpty(country2))
        {
            return BadRequest("Необходимо указать обе страны");
        }

        var data = await _dataService.GetComparisonDataAsync(country1, country2);
        return Ok(data);
    }

    [HttpGet("compare-by-category")]
    public async Task<ActionResult<IEnumerable<InflationData>>> CompareByCategory(
    [FromQuery] string country1,
    [FromQuery] string country2,
    [FromQuery] string category)
    {
        try
        {
            if (string.IsNullOrEmpty(country1) || string.IsNullOrEmpty(country2) || string.IsNullOrEmpty(category))
            {
                return BadRequest("Все параметры обязательны");
            }

            var data = await _dataService.GetCategoryComparisonAsync(country1, country2, category);

            if (data == null || !data.Any())
            {
                return NotFound("Данные не найдены");
            }

            return Ok(data);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"Ошибка сервера: {ex.Message}");
        }
    }

    [HttpGet("rate")]
    public async Task<IActionResult> Rate([FromQuery] string country, [FromQuery] int startYear, [FromQuery] int endYear)
    {
        int result = await _dataService.GetInflationCalculateResult(country, startYear, endYear);
        return Ok(new { Rate = result });
    }
}