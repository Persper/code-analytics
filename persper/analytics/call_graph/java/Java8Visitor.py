# Generated from Java8.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .Java8Parser import Java8Parser
else:
    from Java8Parser import Java8Parser

# This class defines a complete generic visitor for a parse tree produced by Java8Parser.

class Java8Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by Java8Parser#literal.
    def visitLiteral(self, ctx:Java8Parser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primitiveType.
    def visitPrimitiveType(self, ctx:Java8Parser.PrimitiveTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#numericType.
    def visitNumericType(self, ctx:Java8Parser.NumericTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#integralType.
    def visitIntegralType(self, ctx:Java8Parser.IntegralTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#floatingPointType.
    def visitFloatingPointType(self, ctx:Java8Parser.FloatingPointTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#referenceType.
    def visitReferenceType(self, ctx:Java8Parser.ReferenceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classOrInterfaceType.
    def visitClassOrInterfaceType(self, ctx:Java8Parser.ClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classType.
    def visitClassType(self, ctx:Java8Parser.ClassTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classType_lf_classOrInterfaceType.
    def visitClassType_lf_classOrInterfaceType(self, ctx:Java8Parser.ClassType_lf_classOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classType_lfno_classOrInterfaceType.
    def visitClassType_lfno_classOrInterfaceType(self, ctx:Java8Parser.ClassType_lfno_classOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceType.
    def visitInterfaceType(self, ctx:Java8Parser.InterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceType_lf_classOrInterfaceType.
    def visitInterfaceType_lf_classOrInterfaceType(self, ctx:Java8Parser.InterfaceType_lf_classOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceType_lfno_classOrInterfaceType.
    def visitInterfaceType_lfno_classOrInterfaceType(self, ctx:Java8Parser.InterfaceType_lfno_classOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeVariable.
    def visitTypeVariable(self, ctx:Java8Parser.TypeVariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#arrayType.
    def visitArrayType(self, ctx:Java8Parser.ArrayTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#dims.
    def visitDims(self, ctx:Java8Parser.DimsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeParameter.
    def visitTypeParameter(self, ctx:Java8Parser.TypeParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeParameterModifier.
    def visitTypeParameterModifier(self, ctx:Java8Parser.TypeParameterModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeBound.
    def visitTypeBound(self, ctx:Java8Parser.TypeBoundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#additionalBound.
    def visitAdditionalBound(self, ctx:Java8Parser.AdditionalBoundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeArguments.
    def visitTypeArguments(self, ctx:Java8Parser.TypeArgumentsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeArgumentList.
    def visitTypeArgumentList(self, ctx:Java8Parser.TypeArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeArgument.
    def visitTypeArgument(self, ctx:Java8Parser.TypeArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#wildcard.
    def visitWildcard(self, ctx:Java8Parser.WildcardContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#wildcardBounds.
    def visitWildcardBounds(self, ctx:Java8Parser.WildcardBoundsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#packageName.
    def visitPackageName(self, ctx:Java8Parser.PackageNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeName.
    def visitTypeName(self, ctx:Java8Parser.TypeNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#packageOrTypeName.
    def visitPackageOrTypeName(self, ctx:Java8Parser.PackageOrTypeNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#expressionName.
    def visitExpressionName(self, ctx:Java8Parser.ExpressionNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodName.
    def visitMethodName(self, ctx:Java8Parser.MethodNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#ambiguousName.
    def visitAmbiguousName(self, ctx:Java8Parser.AmbiguousNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#compilationUnit.
    def visitCompilationUnit(self, ctx:Java8Parser.CompilationUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#packageDeclaration.
    def visitPackageDeclaration(self, ctx:Java8Parser.PackageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#packageModifier.
    def visitPackageModifier(self, ctx:Java8Parser.PackageModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#importDeclaration.
    def visitImportDeclaration(self, ctx:Java8Parser.ImportDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#singleTypeImportDeclaration.
    def visitSingleTypeImportDeclaration(self, ctx:Java8Parser.SingleTypeImportDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeImportOnDemandDeclaration.
    def visitTypeImportOnDemandDeclaration(self, ctx:Java8Parser.TypeImportOnDemandDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#singleStaticImportDeclaration.
    def visitSingleStaticImportDeclaration(self, ctx:Java8Parser.SingleStaticImportDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#staticImportOnDemandDeclaration.
    def visitStaticImportOnDemandDeclaration(self, ctx:Java8Parser.StaticImportOnDemandDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeDeclaration.
    def visitTypeDeclaration(self, ctx:Java8Parser.TypeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classDeclaration.
    def visitClassDeclaration(self, ctx:Java8Parser.ClassDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#normalClassDeclaration.
    def visitNormalClassDeclaration(self, ctx:Java8Parser.NormalClassDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classModifier.
    def visitClassModifier(self, ctx:Java8Parser.ClassModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeParameters.
    def visitTypeParameters(self, ctx:Java8Parser.TypeParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeParameterList.
    def visitTypeParameterList(self, ctx:Java8Parser.TypeParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#superclass.
    def visitSuperclass(self, ctx:Java8Parser.SuperclassContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#superinterfaces.
    def visitSuperinterfaces(self, ctx:Java8Parser.SuperinterfacesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceTypeList.
    def visitInterfaceTypeList(self, ctx:Java8Parser.InterfaceTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classBody.
    def visitClassBody(self, ctx:Java8Parser.ClassBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classBodyDeclaration.
    def visitClassBodyDeclaration(self, ctx:Java8Parser.ClassBodyDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classMemberDeclaration.
    def visitClassMemberDeclaration(self, ctx:Java8Parser.ClassMemberDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#fieldDeclaration.
    def visitFieldDeclaration(self, ctx:Java8Parser.FieldDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#fieldModifier.
    def visitFieldModifier(self, ctx:Java8Parser.FieldModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#variableDeclaratorList.
    def visitVariableDeclaratorList(self, ctx:Java8Parser.VariableDeclaratorListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#variableDeclarator.
    def visitVariableDeclarator(self, ctx:Java8Parser.VariableDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#variableDeclaratorId.
    def visitVariableDeclaratorId(self, ctx:Java8Parser.VariableDeclaratorIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#variableInitializer.
    def visitVariableInitializer(self, ctx:Java8Parser.VariableInitializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannType.
    def visitUnannType(self, ctx:Java8Parser.UnannTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannPrimitiveType.
    def visitUnannPrimitiveType(self, ctx:Java8Parser.UnannPrimitiveTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannReferenceType.
    def visitUnannReferenceType(self, ctx:Java8Parser.UnannReferenceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannClassOrInterfaceType.
    def visitUnannClassOrInterfaceType(self, ctx:Java8Parser.UnannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannClassType.
    def visitUnannClassType(self, ctx:Java8Parser.UnannClassTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannClassType_lf_unannClassOrInterfaceType.
    def visitUnannClassType_lf_unannClassOrInterfaceType(self, ctx:Java8Parser.UnannClassType_lf_unannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannClassType_lfno_unannClassOrInterfaceType.
    def visitUnannClassType_lfno_unannClassOrInterfaceType(self, ctx:Java8Parser.UnannClassType_lfno_unannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannInterfaceType.
    def visitUnannInterfaceType(self, ctx:Java8Parser.UnannInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannInterfaceType_lf_unannClassOrInterfaceType.
    def visitUnannInterfaceType_lf_unannClassOrInterfaceType(self, ctx:Java8Parser.UnannInterfaceType_lf_unannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannInterfaceType_lfno_unannClassOrInterfaceType.
    def visitUnannInterfaceType_lfno_unannClassOrInterfaceType(self, ctx:Java8Parser.UnannInterfaceType_lfno_unannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannTypeVariable.
    def visitUnannTypeVariable(self, ctx:Java8Parser.UnannTypeVariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unannArrayType.
    def visitUnannArrayType(self, ctx:Java8Parser.UnannArrayTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodDeclaration.
    def visitMethodDeclaration(self, ctx:Java8Parser.MethodDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodModifier.
    def visitMethodModifier(self, ctx:Java8Parser.MethodModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodHeader.
    def visitMethodHeader(self, ctx:Java8Parser.MethodHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#result.
    def visitResult(self, ctx:Java8Parser.ResultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodDeclarator.
    def visitMethodDeclarator(self, ctx:Java8Parser.MethodDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#formalParameterList.
    def visitFormalParameterList(self, ctx:Java8Parser.FormalParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#formalParameters.
    def visitFormalParameters(self, ctx:Java8Parser.FormalParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#formalParameter.
    def visitFormalParameter(self, ctx:Java8Parser.FormalParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#variableModifier.
    def visitVariableModifier(self, ctx:Java8Parser.VariableModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#lastFormalParameter.
    def visitLastFormalParameter(self, ctx:Java8Parser.LastFormalParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#receiverParameter.
    def visitReceiverParameter(self, ctx:Java8Parser.ReceiverParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#throws_.
    def visitThrows_(self, ctx:Java8Parser.Throws_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#exceptionTypeList.
    def visitExceptionTypeList(self, ctx:Java8Parser.ExceptionTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#exceptionType.
    def visitExceptionType(self, ctx:Java8Parser.ExceptionTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodBody.
    def visitMethodBody(self, ctx:Java8Parser.MethodBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#instanceInitializer.
    def visitInstanceInitializer(self, ctx:Java8Parser.InstanceInitializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#staticInitializer.
    def visitStaticInitializer(self, ctx:Java8Parser.StaticInitializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#constructorDeclaration.
    def visitConstructorDeclaration(self, ctx:Java8Parser.ConstructorDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#constructorModifier.
    def visitConstructorModifier(self, ctx:Java8Parser.ConstructorModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#constructorDeclarator.
    def visitConstructorDeclarator(self, ctx:Java8Parser.ConstructorDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#simpleTypeName.
    def visitSimpleTypeName(self, ctx:Java8Parser.SimpleTypeNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#constructorBody.
    def visitConstructorBody(self, ctx:Java8Parser.ConstructorBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#explicitConstructorInvocation.
    def visitExplicitConstructorInvocation(self, ctx:Java8Parser.ExplicitConstructorInvocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#enumDeclaration.
    def visitEnumDeclaration(self, ctx:Java8Parser.EnumDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#enumBody.
    def visitEnumBody(self, ctx:Java8Parser.EnumBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#enumConstantList.
    def visitEnumConstantList(self, ctx:Java8Parser.EnumConstantListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#enumConstant.
    def visitEnumConstant(self, ctx:Java8Parser.EnumConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#enumConstantModifier.
    def visitEnumConstantModifier(self, ctx:Java8Parser.EnumConstantModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#enumBodyDeclarations.
    def visitEnumBodyDeclarations(self, ctx:Java8Parser.EnumBodyDeclarationsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceDeclaration.
    def visitInterfaceDeclaration(self, ctx:Java8Parser.InterfaceDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#normalInterfaceDeclaration.
    def visitNormalInterfaceDeclaration(self, ctx:Java8Parser.NormalInterfaceDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceModifier.
    def visitInterfaceModifier(self, ctx:Java8Parser.InterfaceModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#extendsInterfaces.
    def visitExtendsInterfaces(self, ctx:Java8Parser.ExtendsInterfacesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceBody.
    def visitInterfaceBody(self, ctx:Java8Parser.InterfaceBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceMemberDeclaration.
    def visitInterfaceMemberDeclaration(self, ctx:Java8Parser.InterfaceMemberDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#constantDeclaration.
    def visitConstantDeclaration(self, ctx:Java8Parser.ConstantDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#constantModifier.
    def visitConstantModifier(self, ctx:Java8Parser.ConstantModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceMethodDeclaration.
    def visitInterfaceMethodDeclaration(self, ctx:Java8Parser.InterfaceMethodDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#interfaceMethodModifier.
    def visitInterfaceMethodModifier(self, ctx:Java8Parser.InterfaceMethodModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#annotationTypeDeclaration.
    def visitAnnotationTypeDeclaration(self, ctx:Java8Parser.AnnotationTypeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#annotationTypeBody.
    def visitAnnotationTypeBody(self, ctx:Java8Parser.AnnotationTypeBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#annotationTypeMemberDeclaration.
    def visitAnnotationTypeMemberDeclaration(self, ctx:Java8Parser.AnnotationTypeMemberDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#annotationTypeElementDeclaration.
    def visitAnnotationTypeElementDeclaration(self, ctx:Java8Parser.AnnotationTypeElementDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#annotationTypeElementModifier.
    def visitAnnotationTypeElementModifier(self, ctx:Java8Parser.AnnotationTypeElementModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#defaultValue.
    def visitDefaultValue(self, ctx:Java8Parser.DefaultValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#annotation.
    def visitAnnotation(self, ctx:Java8Parser.AnnotationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#normalAnnotation.
    def visitNormalAnnotation(self, ctx:Java8Parser.NormalAnnotationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#elementValuePairList.
    def visitElementValuePairList(self, ctx:Java8Parser.ElementValuePairListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#elementValuePair.
    def visitElementValuePair(self, ctx:Java8Parser.ElementValuePairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#elementValue.
    def visitElementValue(self, ctx:Java8Parser.ElementValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#elementValueArrayInitializer.
    def visitElementValueArrayInitializer(self, ctx:Java8Parser.ElementValueArrayInitializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#elementValueList.
    def visitElementValueList(self, ctx:Java8Parser.ElementValueListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#markerAnnotation.
    def visitMarkerAnnotation(self, ctx:Java8Parser.MarkerAnnotationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#singleElementAnnotation.
    def visitSingleElementAnnotation(self, ctx:Java8Parser.SingleElementAnnotationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#arrayInitializer.
    def visitArrayInitializer(self, ctx:Java8Parser.ArrayInitializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#variableInitializerList.
    def visitVariableInitializerList(self, ctx:Java8Parser.VariableInitializerListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#block.
    def visitBlock(self, ctx:Java8Parser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#blockStatements.
    def visitBlockStatements(self, ctx:Java8Parser.BlockStatementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#blockStatement.
    def visitBlockStatement(self, ctx:Java8Parser.BlockStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#localVariableDeclarationStatement.
    def visitLocalVariableDeclarationStatement(self, ctx:Java8Parser.LocalVariableDeclarationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#localVariableDeclaration.
    def visitLocalVariableDeclaration(self, ctx:Java8Parser.LocalVariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#statement.
    def visitStatement(self, ctx:Java8Parser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#statementNoShortIf.
    def visitStatementNoShortIf(self, ctx:Java8Parser.StatementNoShortIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#statementWithoutTrailingSubstatement.
    def visitStatementWithoutTrailingSubstatement(self, ctx:Java8Parser.StatementWithoutTrailingSubstatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#emptyStatement.
    def visitEmptyStatement(self, ctx:Java8Parser.EmptyStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#labeledStatement.
    def visitLabeledStatement(self, ctx:Java8Parser.LabeledStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#labeledStatementNoShortIf.
    def visitLabeledStatementNoShortIf(self, ctx:Java8Parser.LabeledStatementNoShortIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#expressionStatement.
    def visitExpressionStatement(self, ctx:Java8Parser.ExpressionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#statementExpression.
    def visitStatementExpression(self, ctx:Java8Parser.StatementExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#ifThenStatement.
    def visitIfThenStatement(self, ctx:Java8Parser.IfThenStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#ifThenElseStatement.
    def visitIfThenElseStatement(self, ctx:Java8Parser.IfThenElseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#ifThenElseStatementNoShortIf.
    def visitIfThenElseStatementNoShortIf(self, ctx:Java8Parser.IfThenElseStatementNoShortIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#assertStatement.
    def visitAssertStatement(self, ctx:Java8Parser.AssertStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#switchStatement.
    def visitSwitchStatement(self, ctx:Java8Parser.SwitchStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#switchBlock.
    def visitSwitchBlock(self, ctx:Java8Parser.SwitchBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#switchBlockStatementGroup.
    def visitSwitchBlockStatementGroup(self, ctx:Java8Parser.SwitchBlockStatementGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#switchLabels.
    def visitSwitchLabels(self, ctx:Java8Parser.SwitchLabelsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#switchLabel.
    def visitSwitchLabel(self, ctx:Java8Parser.SwitchLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#enumConstantName.
    def visitEnumConstantName(self, ctx:Java8Parser.EnumConstantNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#whileStatement.
    def visitWhileStatement(self, ctx:Java8Parser.WhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#whileStatementNoShortIf.
    def visitWhileStatementNoShortIf(self, ctx:Java8Parser.WhileStatementNoShortIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#doStatement.
    def visitDoStatement(self, ctx:Java8Parser.DoStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#forStatement.
    def visitForStatement(self, ctx:Java8Parser.ForStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#forStatementNoShortIf.
    def visitForStatementNoShortIf(self, ctx:Java8Parser.ForStatementNoShortIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#basicForStatement.
    def visitBasicForStatement(self, ctx:Java8Parser.BasicForStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#basicForStatementNoShortIf.
    def visitBasicForStatementNoShortIf(self, ctx:Java8Parser.BasicForStatementNoShortIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#forInit.
    def visitForInit(self, ctx:Java8Parser.ForInitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#forUpdate.
    def visitForUpdate(self, ctx:Java8Parser.ForUpdateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#statementExpressionList.
    def visitStatementExpressionList(self, ctx:Java8Parser.StatementExpressionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#enhancedForStatement.
    def visitEnhancedForStatement(self, ctx:Java8Parser.EnhancedForStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#enhancedForStatementNoShortIf.
    def visitEnhancedForStatementNoShortIf(self, ctx:Java8Parser.EnhancedForStatementNoShortIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#breakStatement.
    def visitBreakStatement(self, ctx:Java8Parser.BreakStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#continueStatement.
    def visitContinueStatement(self, ctx:Java8Parser.ContinueStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#returnStatement.
    def visitReturnStatement(self, ctx:Java8Parser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#throwStatement.
    def visitThrowStatement(self, ctx:Java8Parser.ThrowStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#synchronizedStatement.
    def visitSynchronizedStatement(self, ctx:Java8Parser.SynchronizedStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#tryStatement.
    def visitTryStatement(self, ctx:Java8Parser.TryStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#catches.
    def visitCatches(self, ctx:Java8Parser.CatchesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#catchClause.
    def visitCatchClause(self, ctx:Java8Parser.CatchClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#catchFormalParameter.
    def visitCatchFormalParameter(self, ctx:Java8Parser.CatchFormalParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#catchType.
    def visitCatchType(self, ctx:Java8Parser.CatchTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#finally_.
    def visitFinally_(self, ctx:Java8Parser.Finally_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#tryWithResourcesStatement.
    def visitTryWithResourcesStatement(self, ctx:Java8Parser.TryWithResourcesStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#resourceSpecification.
    def visitResourceSpecification(self, ctx:Java8Parser.ResourceSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#resourceList.
    def visitResourceList(self, ctx:Java8Parser.ResourceListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#resource.
    def visitResource(self, ctx:Java8Parser.ResourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primary.
    def visitPrimary(self, ctx:Java8Parser.PrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primaryNoNewArray.
    def visitPrimaryNoNewArray(self, ctx:Java8Parser.PrimaryNoNewArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primaryNoNewArray_lf_arrayAccess.
    def visitPrimaryNoNewArray_lf_arrayAccess(self, ctx:Java8Parser.PrimaryNoNewArray_lf_arrayAccessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primaryNoNewArray_lfno_arrayAccess.
    def visitPrimaryNoNewArray_lfno_arrayAccess(self, ctx:Java8Parser.PrimaryNoNewArray_lfno_arrayAccessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primaryNoNewArray_lf_primary.
    def visitPrimaryNoNewArray_lf_primary(self, ctx:Java8Parser.PrimaryNoNewArray_lf_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primaryNoNewArray_lf_primary_lf_arrayAccess_lf_primary.
    def visitPrimaryNoNewArray_lf_primary_lf_arrayAccess_lf_primary(self, ctx:Java8Parser.PrimaryNoNewArray_lf_primary_lf_arrayAccess_lf_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primaryNoNewArray_lf_primary_lfno_arrayAccess_lf_primary.
    def visitPrimaryNoNewArray_lf_primary_lfno_arrayAccess_lf_primary(self, ctx:Java8Parser.PrimaryNoNewArray_lf_primary_lfno_arrayAccess_lf_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primaryNoNewArray_lfno_primary.
    def visitPrimaryNoNewArray_lfno_primary(self, ctx:Java8Parser.PrimaryNoNewArray_lfno_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primaryNoNewArray_lfno_primary_lf_arrayAccess_lfno_primary.
    def visitPrimaryNoNewArray_lfno_primary_lf_arrayAccess_lfno_primary(self, ctx:Java8Parser.PrimaryNoNewArray_lfno_primary_lf_arrayAccess_lfno_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#primaryNoNewArray_lfno_primary_lfno_arrayAccess_lfno_primary.
    def visitPrimaryNoNewArray_lfno_primary_lfno_arrayAccess_lfno_primary(self, ctx:Java8Parser.PrimaryNoNewArray_lfno_primary_lfno_arrayAccess_lfno_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classInstanceCreationExpression.
    def visitClassInstanceCreationExpression(self, ctx:Java8Parser.ClassInstanceCreationExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classInstanceCreationExpression_lf_primary.
    def visitClassInstanceCreationExpression_lf_primary(self, ctx:Java8Parser.ClassInstanceCreationExpression_lf_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#classInstanceCreationExpression_lfno_primary.
    def visitClassInstanceCreationExpression_lfno_primary(self, ctx:Java8Parser.ClassInstanceCreationExpression_lfno_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#typeArgumentsOrDiamond.
    def visitTypeArgumentsOrDiamond(self, ctx:Java8Parser.TypeArgumentsOrDiamondContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#fieldAccess.
    def visitFieldAccess(self, ctx:Java8Parser.FieldAccessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#fieldAccess_lf_primary.
    def visitFieldAccess_lf_primary(self, ctx:Java8Parser.FieldAccess_lf_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#fieldAccess_lfno_primary.
    def visitFieldAccess_lfno_primary(self, ctx:Java8Parser.FieldAccess_lfno_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#arrayAccess.
    def visitArrayAccess(self, ctx:Java8Parser.ArrayAccessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#arrayAccess_lf_primary.
    def visitArrayAccess_lf_primary(self, ctx:Java8Parser.ArrayAccess_lf_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#arrayAccess_lfno_primary.
    def visitArrayAccess_lfno_primary(self, ctx:Java8Parser.ArrayAccess_lfno_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodInvocation.
    def visitMethodInvocation(self, ctx:Java8Parser.MethodInvocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodInvocation_lf_primary.
    def visitMethodInvocation_lf_primary(self, ctx:Java8Parser.MethodInvocation_lf_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodInvocation_lfno_primary.
    def visitMethodInvocation_lfno_primary(self, ctx:Java8Parser.MethodInvocation_lfno_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#argumentList.
    def visitArgumentList(self, ctx:Java8Parser.ArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodReference.
    def visitMethodReference(self, ctx:Java8Parser.MethodReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodReference_lf_primary.
    def visitMethodReference_lf_primary(self, ctx:Java8Parser.MethodReference_lf_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#methodReference_lfno_primary.
    def visitMethodReference_lfno_primary(self, ctx:Java8Parser.MethodReference_lfno_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#arrayCreationExpression.
    def visitArrayCreationExpression(self, ctx:Java8Parser.ArrayCreationExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#dimExprs.
    def visitDimExprs(self, ctx:Java8Parser.DimExprsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#dimExpr.
    def visitDimExpr(self, ctx:Java8Parser.DimExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#constantExpression.
    def visitConstantExpression(self, ctx:Java8Parser.ConstantExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#expression.
    def visitExpression(self, ctx:Java8Parser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#lambdaExpression.
    def visitLambdaExpression(self, ctx:Java8Parser.LambdaExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#lambdaParameters.
    def visitLambdaParameters(self, ctx:Java8Parser.LambdaParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#inferredFormalParameterList.
    def visitInferredFormalParameterList(self, ctx:Java8Parser.InferredFormalParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#lambdaBody.
    def visitLambdaBody(self, ctx:Java8Parser.LambdaBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#assignmentExpression.
    def visitAssignmentExpression(self, ctx:Java8Parser.AssignmentExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#assignment.
    def visitAssignment(self, ctx:Java8Parser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#leftHandSide.
    def visitLeftHandSide(self, ctx:Java8Parser.LeftHandSideContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#assignmentOperator.
    def visitAssignmentOperator(self, ctx:Java8Parser.AssignmentOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#conditionalExpression.
    def visitConditionalExpression(self, ctx:Java8Parser.ConditionalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#conditionalOrExpression.
    def visitConditionalOrExpression(self, ctx:Java8Parser.ConditionalOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#conditionalAndExpression.
    def visitConditionalAndExpression(self, ctx:Java8Parser.ConditionalAndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#inclusiveOrExpression.
    def visitInclusiveOrExpression(self, ctx:Java8Parser.InclusiveOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#exclusiveOrExpression.
    def visitExclusiveOrExpression(self, ctx:Java8Parser.ExclusiveOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#andExpression.
    def visitAndExpression(self, ctx:Java8Parser.AndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#equalityExpression.
    def visitEqualityExpression(self, ctx:Java8Parser.EqualityExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#relationalExpression.
    def visitRelationalExpression(self, ctx:Java8Parser.RelationalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#shiftExpression.
    def visitShiftExpression(self, ctx:Java8Parser.ShiftExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#additiveExpression.
    def visitAdditiveExpression(self, ctx:Java8Parser.AdditiveExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx:Java8Parser.MultiplicativeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unaryExpression.
    def visitUnaryExpression(self, ctx:Java8Parser.UnaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#preIncrementExpression.
    def visitPreIncrementExpression(self, ctx:Java8Parser.PreIncrementExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#preDecrementExpression.
    def visitPreDecrementExpression(self, ctx:Java8Parser.PreDecrementExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#unaryExpressionNotPlusMinus.
    def visitUnaryExpressionNotPlusMinus(self, ctx:Java8Parser.UnaryExpressionNotPlusMinusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#postfixExpression.
    def visitPostfixExpression(self, ctx:Java8Parser.PostfixExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#postIncrementExpression.
    def visitPostIncrementExpression(self, ctx:Java8Parser.PostIncrementExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#postIncrementExpression_lf_postfixExpression.
    def visitPostIncrementExpression_lf_postfixExpression(self, ctx:Java8Parser.PostIncrementExpression_lf_postfixExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#postDecrementExpression.
    def visitPostDecrementExpression(self, ctx:Java8Parser.PostDecrementExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#postDecrementExpression_lf_postfixExpression.
    def visitPostDecrementExpression_lf_postfixExpression(self, ctx:Java8Parser.PostDecrementExpression_lf_postfixExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Java8Parser#castExpression.
    def visitCastExpression(self, ctx:Java8Parser.CastExpressionContext):
        return self.visitChildren(ctx)



del Java8Parser