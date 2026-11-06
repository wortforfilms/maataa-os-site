// MAATAA OS concept enclosures: shared library (OpenSCAD 2021+). Units: mm.
// Concept only: not a product. Sizes are placeholders until a real board exists.
// Licence: CC BY 4.0, ALL B Vegan Private Limited.
$fn = 48;
wall  = 2.2;     // shell wall
floor_t = 2.4;   // base floor
lid_t = 2.4;     // lid plate
lip   = 2.0;     // lid lip depth
gap   = 0.25;    // print clearance per side
insert_d = 4.2;  // M3 heat-set insert hole
boss_d = 8;
screw_d = 3.4;   // M3 clearance
head_d = 6.2;    // M3 countersink/counterbore

module rbox(l, w, h, r=4) {
  hull() for (x=[r, l-r], y=[r, w-r]) translate([x, y, 0]) cylinder(r=r, h=h);
}
// open-top shell, origin at outer corner
module shell(l, w, h, r=4) {
  difference() {
    rbox(l, w, h, r);
    translate([wall, wall, floor_t]) rbox(l-2*wall, w-2*wall, h, max(r-wall, 0.6));
  }
}
function boss_pos(l, w, inset=6) = [[inset, inset], [l-inset, inset], [inset, w-inset], [l-inset, w-inset]];
module bosses(l, w, h, inset=6) {
  for (p = boss_pos(l, w, inset)) translate([p[0], p[1], 0]) difference() {
    cylinder(d=boss_d, h=h-lid_t);
    translate([0, 0, floor_t]) cylinder(d=insert_d, h=h);
  }
}
module lid(l, w, r=4, inset=6, label="MAATAA OS") {
  difference() {
    union() {
      rbox(l, w, lid_t, r);
      // lip that keys into the shell
      translate([wall+gap, wall+gap, -lip]) difference() {
        rbox(l-2*(wall+gap), w-2*(wall+gap), lip, max(r-wall, 0.6));
        translate([1.6, 1.6, -0.1]) rbox(l-2*(wall+gap)-3.2, w-2*(wall+gap)-3.2, lip+0.2, 0.6);
      }
    }
    for (p = boss_pos(l, w, inset)) translate([p[0], p[1], -lip-1]) {
      cylinder(d=screw_d, h=lid_t+lip+2);
      translate([0, 0, lip+1+lid_t-1.6]) cylinder(d=head_d, h=2);
    }
    // corner relief so the lip clears the bosses
    for (p = boss_pos(l, w, inset)) translate([p[0], p[1], -lip-0.1]) cylinder(d=boss_d+1, h=lip+0.1);
    if (label != "") translate([l/2, w/2, lid_t-0.6])
      linear_extrude(1) text(label, size=min(l, w)/9, halign="center", valign="center");
  }
}
// placeholder PCB (shown in renders only)
module pcb(l, w, t=1.6) color("#2E7D4F") cube([l, w, t]);
// 35 mm DIN rail clip (EN 60715), printed: test the fit on your rail before use
module din_clip(w, depth=7) {
  // fixed hook at top, flexible latch at bottom; rail runs along X
  translate([0, 0, -depth]) difference() {
    cube([w, 45, depth]);
    translate([-1, 5, -0.1]) cube([w+2, 35.4, depth-2.2]);   // rail channel
    translate([-1, 5-1.4, -0.1]) cube([w+2, 1.5, 1.2]);      // top hook undercut
  }
  // latch tongue with a slot for a screwdriver
  translate([w/2-6, 40.4, -depth]) difference() {
    cube([12, 9, 1.6]);
    translate([3, 5, -0.1]) cube([6, 2, 2]);
  }
}
module slot(l, h) cube([l, wall*3, h]);
