#pragma once

#include "CoreMinimal.h"
#include "IKRigDecoder.generated.h"

/** A decoder of the IKRig */
UCLASS(Blueprintable)
class IKRIG_EXAMPLE_API UIKRigDecoder : public UObject {
	GENERATED_BODY()

public:
	UIKRigDecoder();
	~UIKRigDecoder();

	UFUNCTION(BlueprintCallable)
		void DefineSkeletonProportions(
			float InHipsHeight,
			float InSpineLength,
			float InNeckLength,
			float InLeftLegLength,
			float InRightLegLength,
			float InLeftArmLength,
			float InRightArmLength,
			FVector InNeckRootOffset,
			FVector InLeftLegRootOffset,
			FVector InRightLegRootOffset,
			FVector InLeftArmRootOffset,
			FVector InRightArmRootOffset
		);

	UFUNCTION(BlueprintCallable)
		void DecodePose(const TArray<float> EncodedPoseInput);

	UFUNCTION(BlueprintCallable)
		TArray<FVector> GetLimbRootPositions();

	UFUNCTION(BlueprintCallable)
		TArray<FVector> GetLimbDirectionVectors();

	UFUNCTION(BlueprintCallable)
		TArray<FTransform> GetLimbEffectorTransforms();


private:
	/** Character pose in the IKRig encoding format */
	TArray<float> EncodedPose;

	/** Hips height to the floor in cm */
	float HipsHeight;
	/** Length of body parts in cm */
	float SpineLength;
	float NeckLength;
	float LeftLegLength;
	float RightLegLength;
	float LeftArmLength;
	float RightArmLength;
	FVector NeckRootOffset;
	FVector LeftLegRootOffset;
	FVector RightLegRootOffset;
	FVector LeftArmRootOffset;
	FVector RightArmRootOffset;

	FVector SpineRootPosition;
	FVector SpineDirectionVector;
	FTransform SpineEffectorTransform;
	FVector NeckRootPosition;
	FVector NeckDirectionVector;
	FTransform NeckEffectorTransform;
	FVector LeftLegRootPosition;
	FVector LeftLegDirectionVector;
	FTransform LeftLegEffectorTransform;
	FVector RightLegRootPosition;
	FVector RightLegDirectionVector;
	FTransform RightLegEffectorTransform;
	FVector LeftArmRootPosition;
	FVector LeftArmDirectionVector;
	FTransform LeftArmEffectorTransform;
	FVector RightArmRootPosition;
	FVector RightArmDirectionVector;
	FTransform RightArmEffectorTransform;

	FTransform GlobalTransform;

	FVector MayaToUnrealFVector(float x, float y, float z);
	void DecodeLimb(
		FVector &OutRootPosition,
		FVector &OutLimbDirection,
		FTransform &OutEffectorTransform,
		const TArray<float> EncodedPose,
		const int InitialIndex,
		const bool isSpine,
		const FTransform ParentTransform,
		const FVector RootOffset,
		const float HipsHeight,
		const float LimbSize
	);

};
