# Game UI Skill

## Purpose
Build interactive game UI screens using HTML/CSS/JS. Specialized for football management games.

## Common patterns

### Screens to build
1. **Home/Menu** - Team selection, navigation
2. **Squad** - View players, select starting XI, substitutions
3. **Match** - Animated text commentary, scoreboard, time display
4. **Standings** - League table with positions, points, GD
5. **Schedule** - Round-by-round match list with results

### Color palette (football theme)
- Primary: Green pitch (#1a6b3c)
- Secondary: Gold (#f5c518)
- Background: Dark (#1a1a2e) or Grass gradient
- Text: White (#ffffff), Light gray (#e0e0e0)
- Accent: Red (#e63946) for goals/highlights

### Layout guidelines
- Use a single-page application pattern with tab navigation
- Match screen should scroll through events with animation
- Squad screen: grid of player cards, position-grouped
- Standings: clean table with zebra striping
- Mobile-first responsive design

### Tech
- React 18 via CDN or vanilla JS
- CSS Grid/Flexbox for layout
- Fetch API to communicate with Python backend
- No build step needed (CDN imports)
