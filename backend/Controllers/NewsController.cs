using InflationComparison.Models;
using InflationComparison.Services;
using Microsoft.AspNetCore.Mvc;

namespace InflationComparison.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class NewsController : ControllerBase
    {
        private readonly IDataService _dataService;

        public NewsController(IDataService dataService)
        {
            _dataService = dataService;
        }

        [HttpGet("latest")]
        public async Task<ActionResult<IEnumerable<News>>> GetLatestNews([FromQuery] int limit = 10)
        {
            return Ok(await _dataService.GetLatestNewsAsync(limit));
        }

        [HttpGet("filter")]
        public async Task<IActionResult> Filter(
            [FromQuery] string country) // По умолчанию 3 новости на источник
        {
            if (string.IsNullOrEmpty(country))
            {
                return BadRequest("Необходимо указать источник");
            }

            var news = await _dataService.GetNewsBySourceAsync(country, 3);

            return Ok(news);
        }

        [HttpGet("all-sources")]
        public async Task<ActionResult<IEnumerable<string>>> GetAllSources()
        {
            return Ok(await _dataService.GetAllNewsSourcesAsync());
        }
    }
}