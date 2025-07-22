This application is designed to facilitate the accurate identification of the Sunn pest (_Eurygaster integriceps_),
a major pest of cereal crops, along with other species of the genus _Eurygaster_.
It is intended for plant protection specialists monitoring _E. integriceps_ in overwintering sites during autumn and
spring, as well as in wheat fields following the emergence of adults and prior to harvest. Additionally, it may serve as
a valuable tool for anyone conducting field studies involving insects.

[_Eurygaster integriceps_](https://www.gbif.org/species/9157433), a member of the shield bug family Scutelleridae, has
earned notoriety as a major pest of wheat
barley, and oats across North Africa, Eastern Europe, Western Asia, and Central Asia. Notably, this species is included
in Russia's "List of Particularly Dangerous Harmful Organisms for Plant Production." _Eurygaster integriceps_ is a
highly
polymorphic species that strongly resembles [_E. maura_](https://www.gbif.org/species/5758789)
and [_E. testudinaria_](https://www.gbif.org/species/5758794) in its
overall appearance. These three species
are often co-located within wheat cultivation regions. While _E. maura_, or the tortoise bug, may pose a threat to
crops,
its presence on wheat crops remains significantly lower compared to _E. integriceps_. In contrast, _E. testudinaria_,
despite its extensive presence in the Palaearctic region and occasional appearances on wheat fields, has not been
officially registered as a wheat pest. Even experts in plant protection sometimes struggle to differentiate between _E.
integriceps_, _E. maura_, and _E. testudinaria_, which can lead to inaccurate data during monitoring of _E. integriceps_
on
wheat crops and in hibernation sites. This discrepancy impacts the cost and efficacy of protective measures. Among the
three additional species of the genus documented in Europe, Western Asia, or Russia, _E. austriaca_ is sporadically
encountered on wheat crops, while _E. dilaticollis_ and _E. laeviuscula_ are relatively rare and lack economic
significance.

The main damage to wheat is caused by larvae of _Eurygaster integriceps_, especially from the third instar onward, as they
feed on developing grains during the milk and wax ripening stages. A significant challenge is that larvae of _Eurygaster_
species are even more difficult to distinguish than the adult forms. The species identity of larvae can only be
determined through DNA barcoding or indirectly inferred from preharvest monitoring results when adults of the new
generation appear.

Species recognition within the application is carried out using
the [MobileNet V2](https://pytorch.org/hub/pytorch_vision_mobilenet_v2/) convolutional neural network
architecture. The first model performs binary classification, determining whether the uploaded image contains a
representative of the genus _Eurygaster_. If the presence is confirmed, the second model classifies the specimen to the
species level. Each model outputs a distribution of confidence scores indicating the likelihood that the submitted image
belongs to each potential _Eurygaster_ species. It is important to note that a common limitation of modern neural
networks, from the user’s perspective, is their tendency toward "overconfidence." In practical terms, this means that
the confidence scores produced by the models are not inherently calibrated and should not be directly interpreted as
probabilities of correct classification. To address this issue, both models were calibrated using the temperature
scaling method, improving the interpretability of the confidence values.

For model training, the project employed a [dataset](https://doi.org/10.5281/zenodo.15260200) comprising specimen images
from the collection of the [Zoological
Institute](https://zin.ru/index_en.html), St. Petersburg, as well as publicly available datasets from platforms such as
[iNaturalist](https://eurygaster.ru/www.inaturalist.org) and [MacroID](https://eurygaster.ru/www.macroid.ru). The
images were captured using a variety of devices, including a professional imaging system, a compact camera, and a
smartphone (more than 5 000 images).
