# Sistema Immagini Piante - Smart Plants

## Come funziona:

Il sistema cerca automaticamente le immagini delle piante nella cartella `plant-images/` usando il nome esatto della specie.

## Nomi file supportati:

### Per ogni specie:
- `<specie>.jpg` o `<specie>.png` - Dove `<specie>` è il tipo esatto della pianta

### Esempi:
- `cactus.jpg` o `cactus.png` - Per piante di tipo "cactus"
- `monstera.jpg` o `monstera.png` - Per piante di tipo "monstera"
- `ficus.jpg` o `ficus.png` - Per piante di tipo "ficus"
- `lavanda.jpg` o `lavanda.png` - Per piante di tipo "lavanda"
- `orchidea.jpg` o `orchidea.png` - Per piante di tipo "orchidea"
- `felce.jpg` o `felce.png` - Per piante di tipo "felce"

### Fallback generico:
- `plant.jpg` - Per tutte le specie senza immagine specifica

## Logica di fallback:

1. **Prima**: Cerca `<specie>.jpg` (es. `cactus.jpg`)
2. **Se fallisce**: Prova `<specie>.png` (es. `cactus.png`)
3. **Se fallisce ancora**: Usa immagine generica (`plant.jpg`)

## Formati supportati:
- ✅ JPG/JPEG
- ✅ PNG
- ✅ WebP

## Dimensioni consigliate:
- **Larghezza**: 300-500px
- **Altezza**: 300-500px
- **Rapporto**: Quadrato (1:1) per migliore visualizzazione

## Come aggiungere immagini:

1. Trova immagini belle delle piante
2. Ridimensiona se necessario
3. Salva con il nome esatto della specie (es. `cactus.jpg`)
4. Le immagini appariranno automaticamente nel frontend!

## Esempio:
Se hai una pianta di tipo "cactus", il sistema cercherà:
1. `/plant-images/cactus.jpg`
2. `/plant-images/cactus.png` (se JPG non trovato)
3. `/plant-images/plant.jpg` (se anche PNG non trovato)
