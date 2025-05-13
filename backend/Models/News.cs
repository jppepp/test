namespace InflationComparison.Models
{
    public class News
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string Date { get; set; }
        public string Link { get; set; }
        public string Source { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}