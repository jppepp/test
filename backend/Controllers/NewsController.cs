using InflationComparison.Models;
using InflationComparison.Services;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Threading.Tasks;

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

        [HttpGet("by-source")]
        public async Task<ActionResult<IEnumerable<News>>> GetNewsBySource(
            [FromQuery] string source,
            [FromQuery] int limit = 3) // По умолчанию 3 новости на источник
        {
            if (string.IsNullOrEmpty(source))
            {
                return BadRequest("Необходимо указать источник");
            }

            return Ok(await _dataService.GetNewsBySourceAsync(source, limit));
        }

        [HttpGet("all-sources")]
        public async Task<ActionResult<IEnumerable<string>>> GetAllSources()
        {
            return Ok(await _dataService.GetAllNewsSourcesAsync());
        }
    }
}