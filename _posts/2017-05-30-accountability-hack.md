---
layout: post
title:  "Accountability Hackathon 2017"
date:   2017-05-30 22:30:00 +0200
categories: hackathon
---

**Summary of our prototype last year and a discussion of the goals that are described by the organizers**

I will be participating in this years' edition of the [Accountability Hack](https://accountabilityhack.nl/). Last year was fun and inspiring. We worked on a prototype called Comparea, which can find and compare different municipalities. You can find the code on [GitHub](https://github.com/Gijs-Koot/gemeente-deler). The idea is that you start with a municipality and some characteristics, for example, Utrecht with crimerate, and then you find municipalities in the Netherlands with similar characteristics, and you can immediately compare them based on something related, let's say how much money they spend on crime prevention, and that would be a fair comparison. The algorithm is implemented with `sklearn.neighbors.NearestNeighbors`, and the actual work in creating the prototype was actually mostly frontend and cleaning up data.

This year we have a bigger team, and we're still considering a new prototype. There is prize money and swag on the line, so of course we'd like to win. This is the goal of the prototypes, as announced by the organizers.

> How can open data be used to assess effectiveness of money and spendings?

Last year's winner was a very slick app called "The Slimste Burger", that tests your knowledge of municipal expenses, and you could play for highscores, and challenge other people. The questions were automatically generated from data, so that was neat.

So what is effective governmental spending and how could we recognize it? Our last year's prototype was built on the idea that municipalities with similar characteristics should spend the same amount, otherwise, something potentially interesting is going on. Which I think is still valid, but it didn't lead to any immediate revelations. Maybe the approach was a bit too broad and abstract, and we should actually focus on a more specific topic such as crime. The simplifying assumption here is that municipalities are comparable, that the crime rate in one municipality is the same crime rate .

Effective spending happens when things get better, and you spend relatively little money on it. The opposite is a bit easier to imagine, where you spend money, but nothing really happens, or things get worse. Municipalities spend more or less what they earn. According to [this site](http://degemeente.nl/hoe-komt-de-gemeente-aan-haar-geld), approximately 40% is direct taxes, and 60% is from the government, and there is a pretty complicated formula in place to determine the exact amount of the latter, and Open State Foundation, the organisers of the Accountability hackathon, wrote a [blogpost](https://accountabilityhack.nl/2017/05/19/de-verdeling-van-het-gemeentefonds/) about it.

While spending at least is numeric, effectiveness is hard to measure. Perhaps crime rates or the success youth in terms of employment or education?

I'll follow up with a post about the actual event.

PS Talking about effective spending, we are supposed to use a new social platform, created as part of a Horizon2020 program, that you can find on http://nl-spod.routetopa.eu/. I'm just on the fence on government subsidies, especially spending so much time on a platform such as this one seems a bit pointless. Perhaps it's a good exercise for the people involved. But to create a social platform is almost always a bad idea, right?
