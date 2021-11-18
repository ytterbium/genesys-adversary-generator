# genesys-adversary-generator
A web generator of adversaries for the genesys rpg.

All the data (numbers and description) comes from the Expanded Player Book or the Core Rulebook from FFG.

The data is stored in the file `data.json` and is then used through the script `static_generator.py` to generate the static webpage
`adversary.html` with the templates in `template/`.

To serve this generator, one has simply to serve with a static http server `adversary.html` and the `static/` folder. You should additionnaly install
the Bebas Neue font in the `static/fonts/`. 
You can see this project in production on my [webpage](https://genesys.ytterbium.eu).

The usage should be quite intuitive. For now, there is no direct way to save the generated ennemy, however you could save the url and 
use it to recover your adversary. 
