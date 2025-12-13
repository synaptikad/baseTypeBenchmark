# Périmètre du benchmark

Le dataset v1 portera sur un bâtiment tertiaire de taille conséquente, avec une modélisation inspirée des ontologies Haystack, Brick et RealEstateCore. Les relations couvriront équipements HVAC, zones, espaces, points de mesure et liens fonctionnels.

Deux profils de volumétrie seront fournis pour garantir la reproductibilité sur des contextes différents :
- Profil small : jeu réduit mais représentatif, destiné à observer le comportement à petite échelle.
- Profil large : jeu plus volumineux pour mesurer les effets d'échelle.

Ces profils décrivent uniquement la taille du dataset et la charge ; ils n'impliquent pas un matériel particulier.
Les exécutions de référence sont réalisées sur une infrastructure contrôlée (VPS) afin d'isoler la variable de volumétrie.

Aucune comparaison biaisée ne sera acceptée : chaque moteur recevra une configuration équivalente autant que possible (RAM, stockage, paramètres par défaut), et les optimisations seront documentées.
