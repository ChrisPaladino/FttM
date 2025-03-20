# Face to the Mat - Development Roadmap
## Development Phases

### Phase 1: Core System Refinement (Short-Term)
#### Documentation & Structure
- [x] Create comprehensive README
- [x] Generate system architecture diagrams
- [ ] Reorganize codebase for better modularization

#### Bug Fixes & Stability
- [ ] Fix Submission card handling
- [ ] Correct Helped card resolution
- [ ] Improve tiebreaker logic
- [ ] Handle edge cases in card resolution logic
- [ ] Fix Hot Box wrestler selection logic

#### UI Enhancements
- [ ] Improve game board visualization
- [ ] Add more feedback for game events
- [ ] Enhance log display formatting
- [ ] Make wrestler selection more intuitive
- [ ] Improve Hot Box display and interactions

### Phase 2: Feature Completion (Mid-Term)
#### Hot Box Implementation
- [ ] Add ally/foe data to wrestler JSON
- [ ] Implement full Hot Box mechanics
- [ ] Add interface for managing allies and foes
- [ ] Implement grudge wrestler automatic selection

#### Match Types
- [ ] Implement Test of Strength mechanics
- [ ] Add Wild Card resolution
- [ ] Complete Highlight Reel charts
- [ ] Implement Pre/Post match events
- [ ] Add Submission logic with break holds

#### Special Cards
- [ ] Implement Ref Bump cards
- [ ] Add Highlight Reel cards
- [ ] Create Wild Card events
- [ ] Add specialty move handling

### Phase 3: Game Expansion (Long-Term)
#### Advanced Match Types
- [ ] Tag Team match implementation
- [ ] Cage match mechanics
- [ ] Hardcore match rules
- [ ] Battle Royale system
- [ ] Three-For-All match type

#### Federation Management
- [ ] Tournament system
- [ ] Wrestler ranking
- [ ] Championship tracking
- [ ] Long-term statistic recording
- [ ] Win/loss tracking

#### Career Management
- [ ] Wrestler contracts
- [ ] TV Grade progression system
- [ ] Grudge Grade evolution
- [ ] Aging and retirement mechanics
- [ ] Stable/faction management

### Phase 4: Quality of Life & Advanced Features (Future)
#### Enhanced Visualization
- [ ] Animated moves visualization
- [ ] Improved wrestler representation
- [ ] Custom wrestler images support
- [ ] Match replay system

#### Data Management
- [ ] Wrestler import/export
- [ ] Match history recording
- [ ] Federation save/load functionality
- [ ] Match statistics and analytics

#### Advanced AI
- [ ] AI-driven match booking
- [ ] Automatic storyline generation
- [ ] Rivalries based on match history
- [ ] Automatic TV/Grudge grade adjustments

## Implementation Priorities
### Immediate Tasks
1. Fix critical bugs in Submission, Helped and Test of Strength cards
2. Improve Hot Box UI and functionality
3. Complete basic Wild Card implementation
4. Add better documentation to existing code

### Short-Term Goals (1-3 months)
1. Implement all card types from rulebook
2. Complete match end conditions (pins, finishers, submissions)
3. Add Pre/Post match events
4. Refine the user interface for better usability

### Medium-Term Goals (3-6 months)
1. Implement Tag Team match mechanics
2. Add federation management features
3. Create championship tracking system
4. Implement wrestler progression system

### Long-Term Vision (6+ months)
1. Create a complete wrestling promotion simulation
2. Add AI booking and storyline generation
3. Implement advanced visualization of matches
4. Develop multi-federation competition

## Technical Debt Considerations
### Refactoring Opportunities
- Separate UI logic from game logic more clearly
- Move card handling to a dedicated module
- Create a proper event system for match events
- Implement a logging system instead of print statements

### Performance Improvements
- Optimize card resolution algorithm
- Improve UI rendering performance
- Pre-load wrestler data for faster startup
- Implement better data caching

### Testing Strategy
- Create unit tests for core game mechanics
- Implement integration tests for match simulation
- Add validation for wrestler data
- Create automated UI tests
