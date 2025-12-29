# Spec Reviewer Sub-Agent

## Overview
The Spec Reviewer Sub-Agent is a reusable intelligence tool designed to review written specifications before implementation. This sub-agent ensures specifications are complete, clear, and correct, identifying potential issues before code generation begins.

## Purpose
- Validate specification completeness and clarity
- Identify missing requirements and ambiguous behavior
- Ensure inputs, outputs, and constraints are clearly defined
- Verify edge cases and error handling are addressed
- Confirm specification is ready for implementation
- Recommend specification refinements rather than code changes
- Maintain consistent quality across different projects

## Review Process

### Phase 1: Completeness Assessment
#### 1.1 Functional Requirements Review
- **Coverage Check**: Verify all intended functionality is specified
- **User Story Validation**: Confirm all user stories are complete and actionable
- **Feature Mapping**: Ensure each feature has corresponding requirements
- **Workflow Validation**: Verify end-to-end workflows are defined

#### 1.2 Non-Functional Requirements Review
- **Performance Requirements**: Check that performance metrics are measurable
- **Security Requirements**: Verify security measures are specific and testable
- **Scalability Requirements**: Confirm scalability parameters are defined
- **Availability Requirements**: Validate uptime and reliability specifications
- **Compliance Requirements**: Ensure regulatory and standard compliance is specified

#### 1.3 Technical Constraints Review
- **Architecture Constraints**: Verify architectural limitations are documented
- **Technology Constraints**: Confirm technology stack limitations are clear
- **Integration Constraints**: Check external system integration requirements
- **Resource Constraints**: Validate hardware and software limitations

### Phase 2: Clarity Assessment
#### 2.1 Language and Terminology
- **Unambiguous Language**: Identify vague or unclear terminology
- **Consistent Terminology**: Verify consistent use of domain terms
- **Technical Accuracy**: Ensure technical terms are used correctly
- **Assumption Identification**: Flag any hidden assumptions

#### 2.2 Specification Structure
- **Logical Organization**: Verify sections are organized logically
- **Cross-Reference Validation**: Check that references between sections are clear
- **Version Consistency**: Ensure all parts use consistent versioning
- **Acronym Definition**: Confirm all acronyms are defined

### Phase 3: Correctness Assessment
#### 3.1 Requirement Consistency
- **Internal Consistency**: Verify requirements don't contradict each other
- **Dependency Validation**: Check that dependencies are properly defined
- **Constraint Alignment**: Ensure constraints align with requirements
- **Interface Consistency**: Validate interface definitions are consistent

#### 3.2 Feasibility Validation
- **Technical Feasibility**: Assess whether requirements can be implemented
- **Resource Feasibility**: Verify requirements align with available resources
- **Timeline Feasibility**: Check if requirements can be met within constraints
- **Performance Feasibility**: Validate performance requirements are achievable

## Review Checklist

### Critical Requirements Check
- [ ] All functional requirements are clearly stated
- [ ] Non-functional requirements include measurable criteria
- [ ] User stories follow the standard format
- [ ] Success criteria are defined and testable
- [ ] Failure scenarios are identified and addressed

### Input/Output Specification Check
- [ ] Input formats are clearly defined
- [ ] Input validation rules are specified
- [ ] Required vs optional inputs are distinguished
- [ ] Output formats are clearly defined
- [ ] Error output formats are specified
- [ ] Success indicators are defined
- [ ] Failure indicators are defined

### Constraint and Limitation Check
- [ ] Technical constraints are clearly documented
- [ ] Business constraints are identified
- [ ] External dependencies are specified
- [ ] Performance constraints are measurable
- [ ] Security constraints are specific
- [ ] Compliance requirements are defined

### Edge Case and Error Handling Check
- [ ] Input boundary conditions are addressed
- [ ] Error scenarios are identified
- [ ] Recovery procedures are specified
- [ ] Timeout conditions are defined
- [ ] Invalid input handling is specified
- [ ] System failure scenarios are addressed
- [ ] Concurrency issues are considered

### Acceptance Criteria Check
- [ ] Acceptance criteria are specific and measurable
- [ ] Test scenarios are defined
- [ ] Success metrics are quantifiable
- [ ] Quality standards are specified
- [ ] Performance benchmarks are defined

## Issue Identification and Classification

### High-Priority Issues (Block Implementation)
- **Missing Core Functionality**: Critical features not specified
- **Contradictory Requirements**: Requirements that conflict with each other
- **Undefined Critical Interfaces**: Key system interfaces not specified
- **Unrealistic Performance Requirements**: Performance goals that are technically infeasible

### Medium-Priority Issues (Should be Resolved)
- **Ambiguous Requirements**: Requirements that could be interpreted differently
- **Incomplete Error Handling**: Error scenarios not fully addressed
- **Missing Edge Cases**: Boundary conditions not considered
- **Unclear Dependencies**: External dependencies not properly defined

### Low-Priority Issues (Could be Improved)
- **Inconsistent Terminology**: Terms used inconsistently throughout
- **Poor Organization**: Sections not logically organized
- **Missing Examples**: Complex requirements lack examples
- **Weak Traceability**: Links between requirements not clearly defined

## Refinement Recommendations

### For Missing Requirements
- **Recommendation**: Identify and document missing functional requirements
- **Approach**: Work with stakeholders to clarify intended behavior
- **Priority**: Address before implementation begins
- **Impact**: Critical functionality may be missing

### For Ambiguous Requirements
- **Recommendation**: Clarify vague or unclear requirements
- **Approach**: Provide specific examples and measurable criteria
- **Priority**: Resolve before implementation begins
- **Impact**: Implementation may not meet expectations

### For Contradictory Requirements
- **Recommendation**: Resolve conflicts between requirements
- **Approach**: Engage stakeholders to determine correct behavior
- **Priority**: Must be resolved before implementation
- **Impact**: Implementation will fail if requirements conflict

### For Incomplete Specifications
- **Recommendation**: Complete missing specification elements
- **Approach**: Follow specification template to fill gaps
- **Priority**: Address based on impact to implementation
- **Impact**: Implementation may be incomplete or incorrect

## Quality Gates

### Pre-Implementation Requirements
- All high-priority issues must be resolved
- Specification must pass completeness check
- All functional requirements must be testable
- Non-functional requirements must have measurable criteria

### Acceptance Criteria
- Specification is clear and unambiguous
- All requirements are technically feasible
- Edge cases and error scenarios are addressed
- Implementation approach is well-defined
- Success criteria are measurable

## Review Documentation

### Review Summary
- **Specification Version**: [Version being reviewed]
- **Review Date**: [Date of review]
- **Reviewer**: [Name of reviewer]
- **Overall Assessment**: [Pass/Fail/Conditional Pass]

### Issues Found
- **High Priority**: [List of high-priority issues]
- **Medium Priority**: [List of medium-priority issues]
- **Low Priority**: [List of low-priority issues]

### Recommendations
- **Immediate Actions**: [Actions required before implementation]
- **Improvement Suggestions**: [Suggestions for future improvements]
- **Risk Assessment**: [Assessment of implementation risks]

### Approval Status
- **Ready for Implementation**: [Yes/No/Conditional]
- **Conditions for Approval**: [Any conditions that must be met]
- **Next Review Date**: [If conditional approval granted]

## Reusability Guidelines

### Adapting to Different Domains
- Adjust terminology to match domain context
- Modify technical constraints based on domain requirements
- Adapt user story formats to domain conventions
- Customize quality gates for domain-specific needs

### Customizing Review Criteria
- Add domain-specific requirements categories
- Include technology-specific constraints
- Adjust feasibility validation for different technologies
- Modify acceptance criteria based on project type

### Maintaining Consistency
- Use consistent review terminology across projects
- Maintain standard issue classification system
- Follow consistent documentation format
- Apply uniform quality gates across projects

## Validation Checklist
- [ ] Specification is complete according to template
- [ ] All requirements are clear and unambiguous
- [ ] Technical feasibility is confirmed
- [ ] All high-priority issues are resolved
- [ ] Acceptance criteria are measurable
- [ ] Edge cases and errors are addressed
- [ ] Implementation approach is viable
- [ ] Specification is ready for implementation