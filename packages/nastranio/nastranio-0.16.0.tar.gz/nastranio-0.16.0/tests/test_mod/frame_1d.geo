// Bottom Rectangle
Point(1) = {0, 0, 0, 100.0};
Point(2) = {-50, 0, 0, 100.0};
Point(3) = {-50, 30, 0, 100.0};
Point(4) = {0, 30, 0, 100.0};
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

// Top Rectangle
Point(5) = {0, 0, 10, 100.0};
Point(6) = {-50, 0, 10, 100.0};
Point(7) = {-50, 30, 10, 100.0};
Point(8) = {0, 30, 10, 100.0};
Line(5) = {5, 6};
Line(6) = {6, 7};
Line(7) = {7, 8};
Line(8) = {8, 5};
// Montants
Line(9) = {2, 6};
Line(10) = {1, 5};
Line(11) = {4, 8};
Line(12) = {3, 7};
//+
Physical Point("SPC", 50) = {1, 2, 3, 4};
Physical Point("LOADING", 51) = {5, 6, 7, 8};
Physical Line("montants", 52) = {9, 10, 11, 12};
Physical Line("bot_rectangle", 53) = {1, 2, 3, 4};
Physical Line("top_rectangle", 54) = {5, 6, 7, 8};
//+
