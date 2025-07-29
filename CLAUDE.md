# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Development server (runs on port 8000)
yarn dev

# Build for production
yarn build

# Start production server
yarn start

# Lint code
yarn lint

# Update Python skin database from TypeScript source
cd ai_python && source venv/bin/activate && python convert_skin.py
```

## Project Overview

This is a **ROV (Arena of Valor) Skin Sorter** application built with Nuxt.js 2 and TypeScript. The application allows users to create and manage sortable grids of game character skins with the following features:

- **Grid-based skin organizer**: Create customizable grids (rows/columns) to arrange character skins
- **Visual skin browser**: Browse and select from a comprehensive collection of ROV character skins
- **Import/Export functionality**: Save and load grid configurations as JSON files
- **Image export**: Generate PNG images of created skin grids using html2canvas
- **Skin swapping**: Drag-and-drop style functionality to reorganize skins within the grid
- **Class information**: Built-in categorization system for different skin rarities and types

## Architecture

### Frontend Stack
- **Nuxt.js 2** with TypeScript support
- **Vue.js 2.6** (due to Nuxt 2 compatibility)
- **Bootstrap 4** with **BootstrapVue** for UI components
- **FontAwesome** for icons
- **vue-multiselect** for advanced select dropdowns
- **html2canvas** for image generation

### Key Files Structure
- `pages/index.vue` - Main application page with grid interface
- `lib/skin.ts` - Contains the comprehensive skin database (large file with image mappings)
- `model/rov.ts` - TypeScript interfaces for skin data structures
- `plugins/` - Vue plugin configurations for BootstrapVue and vue-multiselect
- `assets/images/` - Extensive collection of ROV character skin images organized by type

### Data Models
```typescript
interface IRovSkin {
  id: number;
  base?: string;      // Character base name
  name?: string;      // Skin name
  image: string;      // Image path
}

interface IRovSkinOnTable extends IRovSkin {
  key: number;        // Grid position
}
```

## Key Features Implementation

### Grid System
- Dynamic grid sizing (2-24 columns/rows)
- Responsive width control (percentage-based)
- Click-to-select skin positioning
- Visual hover effects and transitions

### Skin Management
- Multi-select dropdown with image previews
- Auto-advance to next grid position after selection
- Skin swapping between grid positions
- Reset and cancel operations

### Export Features
- JSON export/import with timestamp naming
- PNG image generation with transparent background
- Automatic filename generation with timestamps

## Development Notes

### Server Configuration
- Development server runs on `0.0.0.0:8000` for network accessibility
- TypeScript build support enabled
- ESLint configured with Nuxt TypeScript rules

### Styling Approach
- Dark theme UI (`bg-dark`)
- Bootstrap grid system for responsive layout
- Custom CSS for skin grid display and hover effects
- FontAwesome icons throughout the interface

### Thai Language Support
- UI text primarily in Thai language
- Skin classification system includes Thai holiday/seasonal categories
- Error messages and placeholders in Thai

### Asset Management
- Large collection of character skin images in `assets/images/skin/`
- Default fallback images for empty grid positions
- Organized by character names and skin types