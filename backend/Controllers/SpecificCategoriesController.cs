using InflationComparison.Models;
using InflationComparison.Services;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace InflationComparison.Controllers
{
    [ApiController]
    [Route("api/specific-categories")]
    public class SpecificCategoriesController : ControllerBase
    {
        private readonly IDataService _dataService;

        public SpecificCategoriesController(IDataService dataService)
        {
            _dataService = dataService;
        }

        [HttpGet("compare")]
        public async Task<ActionResult<IEnumerable<InflationData>>> Compare(
            [FromQuery] string country1,
            [FromQuery] string country2,
            [FromQuery] string category)
        {
            if (string.IsNullOrEmpty(country1) || string.IsNullOrEmpty(country2) || string.IsNullOrEmpty(category))
            {
                return BadRequest("Все параметры обязательны");
            }

            var data = await _dataService.GetSpecificCategoryDataAsync(country1, country2, category);

            if (data == null || !data.Any())
            {
                return NotFound("Данные не найдены");
            }

            return Ok(data);
        }
    }
}