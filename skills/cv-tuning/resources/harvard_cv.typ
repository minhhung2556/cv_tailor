// Harvard-Style Resume Typst Template
// Replicates the layout, typography, horizontal rules, and section formatting of assets/cv_base.pdf

#let cv(
  name: "LUONG DO MINH HUNG",
  title: "Mobile Architect / Technical Lead",
  contact: "minhhung2556@gmail.com · (+84) 775005110 · Ho Chi Minh City, Vietnam",
  body
) = {
  set page(
    paper: "a4",
    margin: (x: 1.5cm, top: 1.4cm, bottom: 1.4cm),
  )
  
  set text(
    font: ("Times New Roman", "Liberation Serif", "Linux Libertine", "PT Serif", "Georgia", "serif"),
    size: 9.5pt,
    lang: "en",
    fill: rgb("#111111"),
  )
  
  set par(justify: true, leading: 0.52em)

  // Header Section
  align(center)[
    #text(17pt, weight: "bold")[#upper(name)] \
    #v(-3pt)
    #text(10.5pt, weight: "bold")[#title] \
    #v(-2pt)
    #text(8.5pt)[#contact]
  ]

  v(4pt)

  body
}

// Section Header Function
#let cv_section(title) = {
  v(7pt)
  text(10pt, weight: "bold")[#upper(title)]
  v(-5pt)
  line(length: 100%, stroke: 0.6pt + rgb("#333333"))
  v(3pt)
}

// Experience Item Helper
#let cv_experience(
  company: "",
  location: "",
  role: "",
  dates: "",
  bullets: ()
) = {
  v(3pt)
  grid(
    columns: (1fr, auto),
    align: (left, right),
    [ *#company*#if location != "" [, #location] ],
    [ #dates ]
  )
  if role != "" {
    v(-3pt)
    grid(
      columns: (1fr, auto),
      align: (left, right),
      [ #emph(role) ],
      []
    )
  }
  v(-2pt)
  for bullet in bullets {
    [ - #bullet ]
  }
}

// Education / Credentials Helper
#let cv_entry(
  title: "",
  subtitle: "",
  dates: "",
  details: ()
) = {
  v(2pt)
  grid(
    columns: (1fr, auto),
    align: (left, right),
    [ *#title*#if subtitle != "" [ · #emph(subtitle)] ],
    [ #dates ]
  )
  v(-2pt)
  for detail in details {
    [ - #detail ]
  }
}
