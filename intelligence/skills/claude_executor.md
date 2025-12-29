# Claude Code Executor Skill

## Overview
The Claude Code Executor Skill is a reusable intelligence tool that ensures safe, spec-driven code generation using Claude Code. This skill enforces strict adherence to approved specifications and prevents manual coding interventions that could compromise the spec-driven development process.

## Purpose
- Ensure all code generation follows approved specifications only
- Prevent manual coding outside of Claude Code execution
- Maintain consistency between specifications and implementation
- Validate specification completeness before code generation
- Guide users to refine specifications rather than modify code directly
- Maintain project structure and architectural constraints

## Execution Principles

### 1. Specification-Only Input
- **Mandatory Input**: Only finalized and reviewed specifications are accepted
- **Validation Check**: Verify that specifications are complete and unambiguous
- **Refusal Protocol**: Reject any request that includes manual code snippets or direct modification instructions
- **Traceability**: Maintain clear link between specification items and generated code

### 2. Claude Code-Only Generation
- **Tool Exclusivity**: Use Claude Code for all code generation activities
- **No Manual Overrides**: Prohibit any manual editing of generated code
- **Template Adherence**: Follow established project templates and patterns
- **Quality Assurance**: Ensure generated code meets specification requirements

### 3. Specification Compliance
- **Strict Adherence**: Generated code must implement exactly what's specified
- **No Extrapolation**: Do not add features or functionality beyond the specification
- **Constraint Respect**: Honor all architectural, performance, and security constraints
- **Requirement Verification**: Confirm each specification requirement is addressed

## Execution Workflow

### Phase 1: Specification Validation
#### 1.1 Completeness Check
- Verify all functional requirements are clearly defined
- Ensure non-functional requirements include measurable criteria
- Confirm input/output specifications are complete
- Validate that edge cases and error scenarios are documented
- Check that acceptance criteria are testable

#### 1.2 Ambiguity Assessment
- Identify any unclear or ambiguous requirements
- Flag missing dependencies or constraints
- Highlight potential conflicts in the specification
- Request clarification for any uncertain elements

#### 1.3 Approval Verification
- Confirm specification has been reviewed by appropriate stakeholders
- Verify specification follows established template standards
- Ensure change management process was followed (if applicable)
- Check for version consistency and approval signatures

### Phase 2: Generation Readiness
#### 2.1 Project Structure Validation
- Verify target project structure matches specification requirements
- Confirm file naming conventions and directory structure
- Validate dependency management approach
- Check build and deployment configuration

#### 2.2 Constraint Verification
- Validate technical constraints are feasible
- Confirm performance requirements are achievable
- Verify security requirements are properly specified
- Check compliance requirements are clearly defined

### Phase 3: Code Generation
#### 3.1 Generation Process
- Execute Claude Code with specification as primary input
- Follow established project patterns and conventions
- Implement error handling as specified
- Include appropriate logging and monitoring

#### 3.2 Quality Assurance
- Verify generated code matches specification requirements
- Confirm code follows project architecture patterns
- Validate security and performance considerations
- Check for proper error handling and edge case coverage

## Refusal Guidelines

### When to Refuse Code Generation
1. **Incomplete Specifications**: If any critical requirements are missing
2. **Ambiguous Requirements**: If requirements are unclear or contradictory
3. **Missing Constraints**: If architectural or technical constraints are undefined
4. **Unauthorized Changes**: If user requests modifications outside the specification
5. **Manual Code Requests**: If user attempts to provide manual code snippets

### Response Protocol for Refusals
- Politely decline the code generation request
- Clearly explain why the request cannot be fulfilled
- Provide specific guidance on specification improvements needed
- Offer to assist with specification refinement
- Refer back to the specification for clarification

## Quality Control Measures

### 1. Specification Alignment
- Each generated component maps to specific specification items
- Generated code includes references to relevant specification sections
- Verification checklist confirms all requirements are addressed
- Traceability matrix links code to specification elements

### 2. Architecture Compliance
- Generated code follows established architectural patterns
- Module boundaries align with specification-defined structure
- Interface definitions match specification requirements
- Data flow conforms to specification design

### 3. Constraint Enforcement
- Performance requirements are implemented as specified
- Security measures match specification requirements
- Scalability features align with specification
- Compliance requirements are properly addressed

## Project Structure Enforcement

### 1. Directory Structure
- Follow specification-defined directory organization
- Maintain consistent naming conventions
- Respect module separation requirements
- Apply appropriate file organization patterns

### 2. Dependency Management
- Use only approved dependencies as specified
- Follow version constraints defined in specification
- Maintain dependency hierarchy as designed
- Apply security considerations for dependencies

### 3. Configuration Management
- Implement configuration as specified in requirements
- Use appropriate configuration patterns for project type
- Ensure environment-specific configurations are handled
- Apply security best practices for configuration

## Specification Refinement Guidance

### When Specifications Need Improvement
- **Clarity Issues**: Provide specific examples of unclear requirements
- **Completeness Gaps**: Identify missing functionality or constraints
- **Feasibility Concerns**: Flag requirements that may not be technically achievable
- **Integration Issues**: Highlight potential conflicts with existing components

### Refinement Assistance
- Suggest specification template improvements
- Recommend requirement clarification techniques
- Provide examples of well-defined requirements
- Guide toward measurable acceptance criteria

## Reusability Guidelines

### Adapting to Different Project Types
1. **Web Applications**: Adjust for frontend/backend architecture
2. **API Services**: Focus on endpoint and data validation patterns
3. **Data Processing**: Emphasize transformation and error handling
4. **Mobile Applications**: Consider platform-specific constraints

### Customization Points
- Modify validation criteria based on project type
- Adjust architectural compliance checks for specific patterns
- Adapt constraint enforcement for different technologies
- Customize quality control measures for project requirements

## Validation Checklist
- [ ] Specification is complete and unambiguous
- [ ] All functional requirements are clearly defined
- [ ] Non-functional requirements include measurable criteria
- [ ] Constraints and dependencies are properly specified
- [ ] Acceptance criteria are testable and achievable
- [ ] Specification has been properly reviewed and approved
- [ ] Project structure matches specification requirements
- [ ] No manual code snippets provided by user
- [ ] Only Claude Code will be used for generation
- [ ] Generated code will strictly follow specification