#include <bits/stdc++.h>
using namespace std;

typedef float latitude;
typedef float longitude;

void sort_tree(vector<pair<latitude, longitude>> &locations, vector<pair<latitude, longitude>>::iterator lp,
               vector<pair<latitude, longitude>>::iterator rp, int *counter)
{
   if (rp - lp <= 1)
      return;

   if (*counter % 2 == 0)
   {
      sort(lp, rp, [](const auto &a, const auto &b)
           { return a.first < b.first; });
   }
   else
   {
      sort(lp, rp, [](const auto &a, const auto &b)
           { return a.second < b.second; });
   }
   (*counter)++;
   auto dist = rp - lp;
   auto mid = lp + dist / 2;
   sort_tree(locations, lp, mid, counter);
   sort_tree(locations, mid + 1, rp, counter);
}

void Build_kd_tree(vector<pair<latitude, longitude>> &locations)
{
   int counter = 0;
   sort_tree(locations, locations.begin(), locations.end(), &counter);
};

class Ktree
{
public:
   vector<pair<latitude, longitude>> locations;
   Ktree(vector<pair<latitude, longitude>> input)
   {
      locations = input;
      Build_kd_tree();
   }
   vector<pair<latitude, longitude>> range_search(latitude min_lat, latitude max_lat,
                                                  longitude min_lon, longitude max_lon)
   {
      vector<pair<latitude, longitude>> result;
      range_search_recursive(locations.begin(), locations.end(), 0,
                             min_lat, max_lat, min_lon, max_lon, result);
      return result;
   }

private:
   void Build_kd_tree()
   {
      int counter = 0;
      sort_tree(locations, locations.begin(), locations.end(), &counter);
   }
   void range_search_recursive(vector<pair<latitude, longitude>>::iterator lp,
                               vector<pair<latitude, longitude>>::iterator rp,
                               int depth,
                               latitude min_lat, latitude max_lat,
                               longitude min_lon, longitude max_lon,
                               vector<pair<latitude, longitude>> &result)
   {
      if (lp >= rp)
         return;

      auto mid = lp + (rp - lp) / 2;
      auto &point = *mid;

      // Check if current point is within range
      if (point.first >= min_lat && point.first <= max_lat &&
          point.second >= min_lon && point.second <= max_lon)
      {
         result.push_back(point);
      }

      if (depth % 2 == 0)
      { // Splitting on latitude
         if (min_lat <= point.first)
         {
            range_search_recursive(lp, mid, depth + 1,
                                   min_lat, max_lat, min_lon, max_lon, result);
         }
         if (max_lat >= point.first)
         {
            range_search_recursive(mid + 1, rp, depth + 1,
                                   min_lat, max_lat, min_lon, max_lon, result);
         }
      }
      else
      { // Splitting on longitude
         if (min_lon <= point.second)
         {
            range_search_recursive(lp, mid, depth + 1,
                                   min_lat, max_lat, min_lon, max_lon, result);
         }
         if (max_lon >= point.second)
         {
            range_search_recursive(mid + 1, rp, depth + 1,
                                   min_lat, max_lat, min_lon, max_lon, result);
         }
      }
   }
};

int main()
{
   // Test Case 1: Basic Sorting and Range Search
   {
      vector<pair<latitude, longitude>> locations = {
          {1.0, 2.0},
          {3.0, 1.0},
          {4.0, 3.0},
          {2.0, 4.0},
          {5.0, 2.0}};

      Ktree tree(locations);
      auto result = tree.range_search(2.0, 4.0, 1.0, 3.0);

      cout << "Test Case 1: Basic KD-Tree" << endl;
      cout << "Points in range (2-4 lat, 1-3 lon): " << result.size() << endl;
      for (auto &p : result)
      {
         cout << "(" << p.first << ", " << p.second << ") ";
      }
      cout << endl
           << endl;
   }

   // Test Case 2: Empty Range Search
   {
      vector<pair<latitude, longitude>> locations = {
          {1.0, 2.0},
          {3.0, 1.0},
          {4.0, 3.0}};

      Ktree tree(locations);
      auto result = tree.range_search(5.0, 6.0, 5.0, 6.0);

      cout << "Test Case 2: Empty Range" << endl;
      cout << "Points in range (5-6 lat, 5-6 lon): " << result.size() << endl;
      cout << endl;
   }

   // Test Case 3: Single Point Range
   {
      vector<pair<latitude, longitude>> locations = {
          {1.0, 2.0},
          {3.0, 1.0},
          {4.0, 3.0}};

      Ktree tree(locations);
      auto result = tree.range_search(3.0, 3.0, 1.0, 1.0);

      cout << "Test Case 3: Single Point Range" << endl;
      cout << "Points in range (3-3 lat, 1-1 lon): " << result.size() << endl;
      for (auto &p : result)
      {
         cout << "(" << p.first << ", " << p.second << ") ";
      }
      cout << endl
           << endl;
   }

   // Test Case 4: Edge Cases
   {
      // Empty tree
      vector<pair<latitude, longitude>> empty;
      Ktree empty_tree(empty);
      auto empty_result = empty_tree.range_search(0, 1, 0, 1);
      cout << "Test Case 4: Edge Cases" << endl;
      cout << "Empty tree range search result size: " << empty_result.size() << endl;

      // Single point tree
      vector<pair<latitude, longitude>> single = {{1.5, 2.5}};
      Ktree single_tree(single);
      auto inside = single_tree.range_search(1.0, 2.0, 2.0, 3.0);
      auto outside = single_tree.range_search(3.0, 4.0, 3.0, 4.0);

      cout << "Single point tree - inside range: " << inside.size() << endl;
      cout << "Single point tree - outside range: " << outside.size() << endl;
      cout << endl;
   }

   // Test Case 5: Large Dataset
   {
      vector<pair<latitude, longitude>> large;
      // Generate 1000 random points between (0,0) and (10,10)
      srand(time(0)); // Seed random number generator
      for (int i = 0; i < 1000; i++)
      {
         large.push_back({static_cast<latitude>(rand() % 100) / 10.0,
                          static_cast<longitude>(rand() % 100) / 10.0});
      }

      Ktree large_tree(large);
      auto result = large_tree.range_search(2.0, 5.0, 3.0, 6.0);

      // Verify all returned points are within range
      bool all_valid = true;
      for (auto &p : result)
      {
         if (p.first < 2.0 || p.first > 5.0 || p.second < 3.0 || p.second > 6.0)
         {
            all_valid = false;
            break;
         }
      }

      cout << "Test Case 5: Large Dataset" << endl;
      cout << "Points in range (2-5 lat, 3-6 lon): " << result.size() << endl;
      cout << "All points in range: " << (all_valid ? "Yes" : "No") << endl;

      // Compare with brute force search
      int brute_count = 0;
      for (auto &p : large)
      {
         if (p.first >= 2.0 && p.first <= 5.0 && p.second >= 3.0 && p.second <= 6.0)
         {
            brute_count++;
         }
      }

      cout << "Brute force count: " << brute_count << endl;
      cout << "KD-Tree count: " << result.size() << endl;
      cout << "Counts match: " << (brute_count == result.size() ? "Yes" : "No") << endl;
   }

   return 0;
}