// Smart plug (Indian Type D socket on a Type D plug): render only, concept.
// Mains device: no print files are published for it. A real one needs a
// flame-retardant moulded housing and BIS / electrical-safety approval.
$fn = 64;
S = 62; D = 40; R = 9;
module body() {
  hull() for (x=[-S/2+R, S/2-R], y=[-S/2+R, S/2-R]) {
    translate([x, y, 0]) cylinder(r=R, h=D-4);
    translate([x, y, D-4]) scale([1, 1, 0.45]) sphere(r=R);
  }
}
module socket_face() {
  // Type D: earth (Ø7.1) above, line and neutral (Ø5.1) 19.1 mm apart
  translate([0, 0, D-1]) {
    translate([0, 9.5, -12]) cylinder(d=8, h=20);
    for (x=[-9.55, 9.55]) translate([x, -5.5, -12]) cylinder(d=5.8, h=20);
  }
}
module pins() {
  color("#C9A55A") {
    translate([0, 9.5, -16]) cylinder(d=7.1, h=16.5);
    for (x=[-9.55, 9.55]) translate([x, -5.5, -14]) cylinder(d=5.1, h=14.5);
  }
}
rotate([0, 0, 0]) {
color("#F1F2F5") difference() {
  body();
  socket_face();
  translate([0, 0, D-0.6]) difference() {   // shallow recess around the socket
    cylinder(d=44, h=3);
    cylinder(d=43, h=3);
  }
  translate([S/2-2, -7.2, D/2-5.2]) cube([3, 14.4, 10.4]);   // side button opening
}
color("#1F2A5C") translate([0, 0, D-0.62]) difference() { cylinder(d=46, h=0.8); cylinder(d=43.5, h=1); }
color("#1F2A5C") translate([S/2-1.6, -7, D/2-5]) cube([2.2, 14, 10]);          // button
color("#FF9A1F") translate([S/2+0.5, -6, D/2+6.5]) cube([0.4, 12, 1.4]);       // status strip
color("#FF9A1F") translate([-S/2+8, -S/2+5, D+0.2]) cube([14, 1.4, 0.6]);      // saffron band
pins();
}
