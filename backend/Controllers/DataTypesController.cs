using System.Collections.Generic;
using System.Threading.Tasks;
using InflationComparison.Models;
using InflationComparison.Services;
using Microsoft.AspNetCore.Mvc;

namespace InflationComparison.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DataTypesController : ControllerBase
    {
        private readonly IDataService _dataService;

        public DataTypesController(IDataService dataService)
        {
            _dataService = dataService;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<DataType>>> GetDataTypes()
        {
            return Ok(await _dataService.GetDataTypesAsync());
        }
    }
}