# Implementation Planner Skill

## Overview
The Implementation Planner Skill is a reusable intelligence tool that transforms written specifications into clear, step-by-step implementation plans. This skill ensures that development efforts follow a logical sequence with well-defined task boundaries and appropriate architectural structure.

## Purpose
- Convert specifications into executable implementation steps
- Define clear task boundaries to prevent scope creep
- Establish appropriate module structure for maintainability
- Minimize over-engineering by focusing on essential components
- Provide a roadmap for development teams
- Ensure alignment between specification and implementation

## Planning Process

### Phase 1: Specification Analysis
#### 1.1 Requirement Categorization
- **Core Features**: Identify essential functionality from functional requirements
- **Supporting Features**: Identify secondary functionality that supports core features
- **Non-Functional Requirements**: Extract performance, security, and scalability requirements
- **Constraints**: Document technical and business constraints

#### 1.2 Dependency Mapping
- Identify dependencies between different functional requirements
- Map external dependencies (APIs, services, libraries)
- Determine order of implementation based on dependencies
- Identify potential integration points

### Phase 2: Architecture Design
#### 2.1 Module Structure Definition
- **Core Modules**: Define modules for primary functionality
- **Utility Modules**: Define modules for common utilities and helpers
- **Interface Modules**: Define modules for user interfaces or API endpoints
- **Data Modules**: Define modules for data handling and persistence
- **Configuration Modules**: Define modules for settings and configuration

#### 2.2 Component Boundaries
- Define clear interfaces between modules
- Establish data flow between components
- Identify shared resources and potential conflicts
- Plan for module reusability and testability

### Phase 3: Implementation Sequencing
#### 3.1 Foundation Tasks
1. **Setup and Configuration**
   - Project scaffolding
   - Development environment setup
   - Build system configuration
   - Testing framework setup

2. **Core Infrastructure**
   - Database schema or data models
   - Authentication and authorization
   - Basic routing and middleware
   - Error handling framework

#### 3.2 Feature Implementation Order
1. **MVP (Minimum Viable Product) Path**
   - Implement the most critical user story first
   - Create end-to-end functionality for core feature
   - Ensure basic workflow is operational

2. **Feature Enhancement**
   - Add supporting features
   - Implement secondary user stories
   - Enhance user experience

3. **Non-Functional Requirements**
   - Performance optimizations
   - Security enhancements
   - Scalability considerations
   - Monitoring and logging

## Implementation Plan Template

### 1. Project Structure
```
project-root/
├── src/                    # Source code
│   ├── modules/           # Feature modules
│   ├── shared/            # Shared utilities
│   ├── config/            # Configuration files
│   └── tests/             # Test files
├── docs/                  # Documentation
├── scripts/               # Build and utility scripts
└── package.json          # Project metadata
```

### 2. Implementation Steps

#### Step 1: [Module Name] - Foundation
- **Objective**: [Brief description of what this step achieves]
- **Files to create**: [List of files to be created]
- **Key tasks**:
  - [Task 1]
  - [Task 2]
  - [Task 3]
- **Acceptance criteria**: [How to verify completion]
- **Dependencies**: [What needs to be completed before this step]

#### Step 2: [Module Name] - Core Functionality
- **Objective**: [Brief description of what this step achieves]
- **Files to modify/create**: [List of files to be modified or created]
- **Key tasks**:
  - [Task 1]
  - [Task 2]
  - [Task 3]
- **Acceptance criteria**: [How to verify completion]
- **Dependencies**: [What needs to be completed before this step]

#### Step n: [Module Name] - Polish and Testing
- **Objective**: [Brief description of what this step achieves]
- **Files to modify**: [List of files to be modified]
- **Key tasks**:
  - [Task 1]
  - [Task 2]
  - [Task 3]
- **Acceptance criteria**: [How to verify completion]
- **Dependencies**: [What needs to be completed before this step]

### 3. Quality Assurance Plan
#### 3.1 Testing Strategy
- **Unit Tests**: [Areas requiring unit tests]
- **Integration Tests**: [Areas requiring integration tests]
- **End-to-End Tests**: [Areas requiring E2E tests]
- **Performance Tests**: [Areas requiring performance testing]

#### 3.2 Code Quality
- **Linting**: [Code style and quality checks to implement]
- **Documentation**: [Documentation requirements]
- **Security**: [Security considerations to address]

### 4. Risk Assessment and Mitigation
#### 4.1 Technical Risks
- **Risk**: [Potential technical challenge]
  - **Impact**: [How this would affect the project]
  - **Mitigation**: [How to address this risk]

#### 4.2 Timeline Risks
- **Risk**: [Potential delay or timeline issue]
  - **Impact**: [How this would affect delivery]
  - **Mitigation**: [How to address this risk]

## Best Practices for Implementation Planning

### 1. Preventing Over-Engineering
- **Start Minimal**: Implement the simplest solution that meets requirements
- **Iterate**: Plan for future enhancements rather than building for every possible future need
- **Focus on Value**: Prioritize features that directly address user needs
- **Avoid Premature Optimization**: Optimize based on actual performance data, not assumptions

### 2. Maintaining Clarity
- **Single Responsibility**: Each module should have a clear, single purpose
- **Clear Interfaces**: Define clean, well-documented interfaces between components
- **Logical Grouping**: Group related functionality together
- **Consistent Naming**: Use consistent naming conventions throughout

### 3. Ensuring Scalability
- **Modular Design**: Design modules to be independently testable and deployable
- **Configuration Over Code**: Use configuration for environment-specific settings
- **Separation of Concerns**: Keep business logic separate from presentation and data access
- **Loose Coupling**: Minimize dependencies between modules

### 4. Planning Considerations
- **Time Estimation**: Plan for testing, debugging, and integration time
- **Resource Allocation**: Consider team skills and availability
- **Review Points**: Build in checkpoints to validate progress
- **Flexibility**: Allow for plan adjustments as understanding deepens

## Reusability Guidelines

### Adapting for Different Project Types
1. **Web Applications**: Focus on frontend/backend separation, API design, and user experience
2. **API Services**: Emphasize endpoint design, authentication, and data validation
3. **Data Processing**: Prioritize data flow, transformation, and error handling
4. **Mobile Applications**: Consider platform-specific considerations and offline capabilities

### Customization Points
- Adjust module structure based on project requirements
- Modify implementation sequence based on dependencies
- Adapt testing strategy to project type
- Customize quality metrics based on project goals

## Validation Checklist
- [ ] All functional requirements are addressed in implementation steps
- [ ] Non-functional requirements are planned for implementation
- [ ] Dependencies between steps are clearly identified
- [ ] Module boundaries are well-defined and logical
- [ ] Risk mitigation strategies are in place
- [ ] Testing approach covers all critical functionality
- [ ] Plan avoids over-engineering while meeting requirements
- [ ] Timeline is realistic for the scope of work