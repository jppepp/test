using InflationComparison.Services;
using Npgsql;

var builder = WebApplication.CreateBuilder(args);

// ��������� ������� � ���������
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// ������������ DataService
builder.Services.AddScoped<IDataService>(provider =>
    new DataService(builder.Configuration.GetConnectionString("DefaultConnection")));

var app = builder.Build();


// ����������� �������� HTTP ��������
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
// ��������� ��� ������� ��� ����������
app.UseCors(builder => builder
    .AllowAnyOrigin()
    .AllowAnyMethod()
    .AllowAnyHeader());
app.UseStaticFiles();
app.MapControllers();

// �������� ����������� � �� ��� ������
try
{
    using var connection = new NpgsqlConnection(builder.Configuration.GetConnectionString("DefaultConnection"));
    connection.Open();
    Console.WriteLine("Successfully connected to PostgreSQL");
}
catch (Exception ex)
{
    Console.WriteLine($"Failed to connect to PostgreSQL: {ex.Message}");
}

try
{
    using var scope = app.Services.CreateScope();
    var dataService = scope.ServiceProvider.GetRequiredService<IDataService>();
    var newsCount = (await dataService.GetLatestNewsAsync(1)).Count();
    Console.WriteLine($"News table contains {newsCount} records");
}
catch (Exception ex)
{
    Console.WriteLine($"Error checking news: {ex.Message}");
}

app.Run();