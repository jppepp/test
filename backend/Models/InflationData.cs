namespace InflationComparison.Models
{
    public class InflationData
    {
        public int Year { get; set; }
        public double? Rate { get; set; }
        public string Country { get; set; }
        public string DataType { get; set; }
        public string Source { get; set; }
    }
}