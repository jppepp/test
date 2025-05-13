using InflationComparison.Models;
using InflationComparison.Services;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace InflationComparison.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CountriesController : ControllerBase
    {
        private readonly IDataService _dataService;

        public CountriesController(IDataService dataService)
        {
            _dataService = dataService;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Country>>> Get()
        {
            var countries = await _dataService.GetCountriesAsync();
            return Ok(countries);
        }
    }
}