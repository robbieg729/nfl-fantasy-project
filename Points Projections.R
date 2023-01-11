library(readxl)

rayleigh <- function(x, t){
  return (t * x * exp(-t/2 * x^2))
}

rayleigh.pred <- function(x, a, b){
  return ((a / b) * x * ((1 + (x^2) / (2 * b))^(-a - 1)))
}

rayleigh.pred.cdf <- function(x, a, b){
  return (1 - (1 + (x^2)/(2*b))^(-a - 1))
}

rayleigh.exp <- function(a, b){
  n <- 10000000
  w <- runif(n)
  f <- (a/b) * ((w^2) / ((1 - w)^4)) * (1 + (w^2) / (2*b*(1-w)^2))^(-a-1)
  return (mean(f))
}

pois.pred <- function(x, a, b){
  return ((b/(b+1))^a * choose(a + x - 1, x) / ((b + 1)^x))
}

pois.exp <- function(a, b){
  x <- seq(0, 30)
  return (sum(x * pois.pred(x, a, b)))
}

norm.pred.cdf <- function(x, m, k, a, b){
  t <- (x - m) / sqrt(b * (1 + k) / (k * a))
  return (pt(t, df=as.integer(2*a)))
}

pass.yds.exp <- function(parameters, year="Total"){
  parameters$Year <- as.factor(parameters$Year)
  return (parameters[parameters$Year == year,]$m)
}

rec.yds.exp <- function(position, parameters, year="Total"){
  parameters$Year <- as.factor(parameters$Year)
  total <- parameters[parameters$Year == year,]
  if (position == "RB"){
    ahat <- total$ahat
    bhat <- total$bhat
    return (ahat/bhat)
  }
  else{
    a <- total$a
    b <- total$b
    return (rayleigh.exp(a, b))
  }
}

rush.yds.exp <- function(position, parameters, year="Total"){
  parameters$Year <- as.factor(parameters$Year)
  total <- parameters[parameters$Year == year,]
  if (position != "RB"){
    ahat <- total$ahat
    bhat <- total$bhat
    return (ahat/bhat)
  }
  else{
    a <- total$a
    b <- total$b
    return (rayleigh.exp(a, b))
  }
}

other.stats.exp <- function(parameters, year="Total"){
  parameters$Year <- as.factor(parameters$Year)
  total <- parameters[parameters$Year == year,]
  a <- total$a
  b <- total$b
  return (pois.exp(a, b))
}

fantasy.points <- function(position, projections, format="PPR"){
  if (position == "QB"){
    return (sum(c(0.04, 4, -2, 0.1, 6, -2) * projections))
  }
  else if (position == "WR" || position == "RB" || position == "TE"){
    if (format == "PPR"){
      return (sum(c(0.1, 6, 1, 0.1, 6, -2) * projections))
    }
    else{
      return (sum(c(0.1, 6, 0, 0.1, 6, -2) * projections))
    }
  }
}

skill.position.fpts <- function(position, path, year="Total", format="PPR"){
  rec.yds <- read_excel(path, sheet="Receiving yards parameters")
  rec <- read_excel(path, sheet="Receptions parameters")
  rec.tds <- read_excel(path, sheet="Receiving touchdowns parameters")
  fumbles <- read_excel(path, sheet="Fumbles lost parameters")
  
  projections <- c(
    0,
    0,
    other.stats.exp(rec, year=year),
    rec.yds.exp(position, rec.yds, year=year),
    other.stats.exp(rec.tds, year=year),
    other.stats.exp(fumbles, year=year)
  )
  
  if (position != "TE"){
    rush.yds <- read_excel(path, sheet="Rushing yards parameters")
    rush.tds <- read_excel(path, sheet="Rushing touchdowns parameters")
    projections[1] <- rush.yds.exp(position, rush.yds, year=year)
    projections[2] <- other.stats.exp(rush.tds, year=year)
  }
  
  return (fantasy.points(position, projections, format))
}

qb.fpts <- function(path, year="Total", format="PPR"){
  pass.yds <- read_excel(path, sheet="Passing yards parameters")
  rush.yds <- read_excel(path, sheet="Rushing yards parameters")
  ints <- read_excel(path, sheet="Interceptions parameters")
  pass.tds <- read_excel(path, sheet="Passing touchdowns parameters")
  rush.tds <- read_excel(path, sheet="Rushing touchdowns parameters")
  fumbles <- read_excel(path, sheet="Fumbles lost parameters")
  
  projections <- c(
    pass.yds.exp(pass.yds, year=year),
    other.stats.exp(pass.tds, year=year),
    other.stats.exp(ints, year=year),
    rush.yds.exp("QB", rush.yds, year=year),
    other.stats.exp(rush.tds, year=year),
    other.stats.exp(fumbles, year=year)
  )
  
  return (fantasy.points("QB", projections, format=format))
}

path <- "Teams/Rams/Offense/WR/Allen Robinson II.xlsx"
qb.fpts(path, year=2021)
skill.position.fpts("WR", path, year="Total")