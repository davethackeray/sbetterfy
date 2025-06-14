# Performance Metrics and Benchmarking Plan for sBetterfy

## Date of Creation
June 14, 2025

## Objective
This document outlines the plan for Task 2.4: Performance Benchmarking from Phase 2 of the 'sBetterfy' project roadmap. The goal is to establish performance benchmarks for key operations (e.g., recommendation generation, playlist creation) using profiling tools, document baseline metrics, and set performance improvement targets. This aligns with the custom instructions to ensure high-quality outputs, optimize performance, and reduce technical debt through thorough documentation.

## Benchmarking Approach
To measure and improve the performance of 'sBetterfy', the following approach will be used:

1. **Identify Key Operations**: Focus on critical user-facing operations that impact experience and system resources:
   - **Recommendation Generation**: Time taken to generate AI-based recommendations using 'recommendation_service.py', including Spotify API calls for verification.
   - **Playlist Creation**: Time taken to create a playlist on Spotify via 'spotify_service.py'.
   - **User Data Retrieval**: Time taken to fetch user data from the database in 'database.py' and decrypt credentials in 'user_service.py'.
   - **API Response Time**: Latency for key API endpoints in 'main.py' (e.g., '/api/recommendations', '/api/create-playlist').

2. **Select Profiling Tools**: Use Python profiling tools to measure execution time and resource usage:
   - **cProfile**: Built-in Python module for detailed function-level profiling to identify bottlenecks in code execution.
   - **timeit**: For micro-benchmarks of small code snippets or specific operations.
   - **psutil**: To monitor system resource usage (CPU, memory) during operations.

3. **Define Test Scenarios**: Create repeatable test scenarios to ensure consistent benchmarking:
   - Simulate a user with a predefined set of liked songs (e.g., 100 songs) for recommendation generation.
   - Use a fixed set of tracks (e.g., 20 tracks) for playlist creation.
   - Test database retrieval with a sample user dataset (e.g., 1,000 user records).
   - Measure API response time under typical load (e.g., single user request).

4. **Establish Baseline Metrics**: Run initial benchmarks to record current performance:
   - Record execution time for each operation (in milliseconds or seconds).
   - Note system resource usage (CPU percentage, memory usage in MB).
   - Document any observed bottlenecks or anomalies.

5. **Set Improvement Targets**: Based on baseline metrics, define realistic performance goals:
   - Reduce recommendation generation time by 20% through further optimizations (e.g., caching additional API calls).
   - Ensure playlist creation completes within 2 seconds for 20 tracks.
   - Target database query response time under 50ms for user data retrieval.
   - Aim for API endpoint latency under 500ms for typical requests.

6. **Document and Iterate**: Record all benchmarking results in this document and update it with each optimization phase to track progress over time.

## Benchmarking Script
Below is a Python script template to perform the benchmarking. This script can be saved as 'benchmark.py' in the project root and run to collect performance data. It uses 'cProfile' for detailed profiling and 'timeit' for specific operation timing.

```python
import cProfile
import pstats
import timeit
import psutil
import os
from spotify_service import SpotifyService
from recommendation_service import RecommendationService
from user_service import UserService
from database import get_db_connection

# Placeholder for user credentials (replace with test data or mock)
TEST_USER_ID = "test_user_id"
TEST_SPOTIFY_CREDS = {"client_id": "test_id", "client_secret": "test_secret"}
TEST_SPOTIFY_TOKENS = {"access_token": "test_access", "refresh_token": "test_refresh"}
TEST_GEMINI_API_KEY = "test_api_key"

def benchmark_recommendation_generation():
    """Benchmark recommendation generation performance"""
    # Initialize services (mock or use test credentials)
    spotify = SpotifyService(TEST_SPOTIFY_CREDS['client_id'], TEST_SPOTIFY_CREDS['client_secret'], TEST_SPOTIFY_TOKENS)
    recommendation_service = RecommendationService(TEST_GEMINI_API_KEY)
    
    # Measure time for recommendation generation
    start_time = timeit.default_timer()
    recommendations = recommendation_service.get_recommendations(spotify, count=20)
    elapsed_time = timeit.default_timer() - start_time
    
    print(f"Recommendation Generation Time: {elapsed_time:.3f} seconds")
    return elapsed_time

def benchmark_playlist_creation():
    """Benchmark playlist creation performance"""
    spotify = SpotifyService(TEST_SPOTIFY_CREDS['client_id'], TEST_SPOTIFY_CREDS['client_secret'], TEST_SPOTIFY_TOKENS)
    test_track_uris = ["spotify:track:test" + str(i) for i in range(20)]
    
    start_time = timeit.default_timer()
    playlist = spotify.create_playlist("Test Playlist", test_track_uris)
    elapsed_time = timeit.default_timer() - start_time
    
    print(f"Playlist Creation Time: {elapsed_time:.3f} seconds")
    return elapsed_time

def benchmark_user_data_retrieval():
    """Benchmark user data retrieval from database"""
    user_service = UserService()
    
    start_time = timeit.default_timer()
    creds = user_service.get_spotify_credentials(TEST_USER_ID)
    elapsed_time = timeit.default_timer() - start_time
    
    print(f"User Data Retrieval Time: {elapsed_time:.3f} seconds")
    return elapsed_time

def measure_system_resources(func, func_name):
    """Measure CPU and memory usage during function execution"""
    process = psutil.Process(os.getpid())
    func()
    cpu_percent = process.cpu_percent(interval=1)
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
    
    print(f"{func_name} - CPU Usage: {cpu_percent:.1f}% | Memory Usage: {memory_mb:.1f} MB")
    return cpu_percent, memory_mb

def run_benchmarks():
    """Run all benchmarks with profiling"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run benchmarks and measure system resources
    rec_time = measure_system_resources(benchmark_recommendation_generation, "Recommendation Generation")
    playlist_time = measure_system_resources(benchmark_playlist_creation, "Playlist Creation")
    user_data_time = measure_system_resources(benchmark_user_data_retrieval, "User Data Retrieval")
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumtime').print_stats(10)  # Print top 10 time-consuming functions
    
    # Summarize results
    print("\nBenchmark Summary:")
    print(f"Recommendation Generation: {rec_time[0]:.3f} s, CPU: {rec_time[1]:.1f}%, Memory: {rec_time[2]:.1f} MB")
    print(f"Playlist Creation: {playlist_time[0]:.3f} s, CPU: {playlist_time[1]:.1f}%, Memory: {playlist_time[2]:.1f} MB")
    print(f"User Data Retrieval: {user_data_time[0]:.3f} s, CPU: {user_data_time[1]:.1f}%, Memory: {user_data_time[2]:.1f} MB")

if __name__ == "__main__":
    run_benchmarks()
```

## Initial Baseline Metrics
As of the creation of this document, no baseline metrics have been established. Once the benchmarking script is run, results will be recorded here in the following format:

- **Recommendation Generation**:
  - Execution Time: TBD seconds
  - CPU Usage: TBD %
  - Memory Usage: TBD MB
  - Bottlenecks: TBD

- **Playlist Creation**:
  - Execution Time: TBD seconds
  - CPU Usage: TBD %
  - Memory Usage: TBD MB
  - Bottlenecks: TBD

- **User Data Retrieval**:
  - Execution Time: TBD seconds
  - CPU Usage: TBD %
  - Memory Usage: TBD MB
  - Bottlenecks: TBD

- **API Response Time (e.g., /api/recommendations)**:
  - Latency: TBD seconds
  - CPU Usage: TBD %
  - Memory Usage: TBD MB
  - Bottlenecks: TBD

## Performance Improvement Targets
Based on the eventual baseline metrics, the following targets are set for future optimization iterations:
- Reduce recommendation generation time by 20% from baseline.
- Ensure playlist creation completes within 2 seconds for 20 tracks.
- Target database query response time under 50ms for user data retrieval.
- Aim for API endpoint latency under 500ms for typical requests.

## Next Steps
1. **Implement Benchmarking Script**: Save the provided script as 'benchmark.py' and adapt it with appropriate test data or mocks for accurate measurement.
2. **Run Initial Benchmarks**: Execute the script to establish baseline metrics and record them in this document.
3. **Identify Bottlenecks**: Analyze profiling output to pinpoint performance bottlenecks for targeted optimization in future tasks.
4. **Update Documentation**: Regularly update this document with new metrics after each optimization phase to track progress towards performance targets.

This plan and script provide a structured approach to performance benchmarking, ensuring that 'sBetterfy' continues to improve in efficiency and scalability as per the roadmap and custom instructions.
