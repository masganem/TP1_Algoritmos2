#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <algorithm>
#include <vector>
#include <utility>
#include <cstdlib>
#include <tuple>

using latitude = float;
using longitude = float;

struct Point {
    latitude lat;
    longitude lon;
    int id;
};

static void sort_tree(std::vector<Point> &locations,
                      std::vector<Point>::iterator lp,
                      std::vector<Point>::iterator rp,
                      int depth)
{
    if (rp - lp <= 1)
        return;

    if (depth % 2 == 0) {
        std::sort(lp, rp, [](const Point &a, const Point &b) { return a.lat < b.lat; });
    } else {
        std::sort(lp, rp, [](const Point &a, const Point &b) { return a.lon < b.lon; });
    }

    auto dist = rp - lp;
    auto mid = lp + dist / 2;
    sort_tree(locations, lp, mid, depth + 1);
    sort_tree(locations, mid + 1, rp, depth + 1);
}

static void Build_kd_tree(std::vector<Point> &locations)
{
    sort_tree(locations, locations.begin(), locations.end(), 0);
}

class KDTreeCPP {
public:
    explicit KDTreeCPP(const std::vector<std::tuple<latitude, longitude, int>> &input)
    {
        locations.reserve(input.size());
        for (const auto &t : input) {
            locations.push_back(Point{std::get<0>(t), std::get<1>(t), std::get<2>(t)});
        }
        Build_kd_tree(locations);
    }

    std::vector<std::tuple<latitude, longitude, int>> range_search(latitude min_lat, latitude max_lat,
                                                                   longitude min_lon, longitude max_lon) const
    {
        std::vector<Point> raw_result;
        range_search_recursive(locations.begin(), locations.end(), 0,
                               min_lat, max_lat, min_lon, max_lon, raw_result);
        std::vector<std::tuple<latitude, longitude, int>> result;
        result.reserve(raw_result.size());
        for (const auto &p : raw_result) {
            result.emplace_back(p.lat, p.lon, p.id);
        }
        return result;
    }

private:
    std::vector<Point> locations;

    static void range_search_recursive(std::vector<Point>::const_iterator lp,
                                       std::vector<Point>::const_iterator rp,
                                       int depth,
                                       latitude min_lat, latitude max_lat,
                                       longitude min_lon, longitude max_lon,
                                       std::vector<Point> &result)
    {
        if (lp >= rp)
            return;

        auto mid = lp + (rp - lp) / 2;
        const Point &point = *mid;

        if (point.lat >= min_lat && point.lat <= max_lat && point.lon >= min_lon && point.lon <= max_lon) {
            result.push_back(point);
        }

        if (depth % 2 == 0) {
            if (min_lat <= point.lat) {
                range_search_recursive(lp, mid, depth + 1, min_lat, max_lat, min_lon, max_lon, result);
            }
            if (max_lat >= point.lat) {
                range_search_recursive(mid + 1, rp, depth + 1, min_lat, max_lat, min_lon, max_lon, result);
            }
        } else {
            if (min_lon <= point.lon) {
                range_search_recursive(lp, mid, depth + 1, min_lat, max_lat, min_lon, max_lon, result);
            }
            if (max_lon >= point.lon) {
                range_search_recursive(mid + 1, rp, depth + 1, min_lat, max_lat, min_lon, max_lon, result);
            }
        }
    }
};

namespace py = pybind11;

PYBIND11_MODULE(kd_tree_cpp, m)
{
    m.doc() = "A simple 2-D KD-Tree with range search that stores (lat, lon, id)";

    py::class_<KDTreeCPP>(m, "KDTreeCPP")
        .def(py::init<const std::vector<std::tuple<latitude, longitude, int>> &>(),
             py::arg("points"),
             "Create a KD-Tree from a list of (lat, lon, id) tuples.")
        .def("range_search", &KDTreeCPP::range_search,
             py::arg("min_lat"), py::arg("max_lat"),
             py::arg("min_lon"), py::arg("max_lon"),
             "Return all points (lat, lon, id) inside the bounding box ([min_lat, max_lat], [min_lon, max_lon]).");
} 
