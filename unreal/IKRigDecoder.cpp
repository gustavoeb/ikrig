#include "IKRigDecoder.h"
#include "CoreMinimal.h"

UIKRigDecoder::UIKRigDecoder()
{
}

UIKRigDecoder::~UIKRigDecoder()
{
}

FVector UIKRigDecoder::MayaToUnrealFVector(float x, float y, float z)
{
	return FVector(x, z, y);
}

void UIKRigDecoder::DecodeLimb(
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
)
{
	FVector LimbRootPosition;
	int idx;
	if (isSpine) {
		LimbRootPosition = MayaToUnrealFVector(EncodedPose[InitialIndex], EncodedPose[InitialIndex + 1], EncodedPose[InitialIndex + 2]);
		LimbRootPosition *= HipsHeight;
		idx = InitialIndex + 3;
	}
	else {
		FQuat RotationOffset(EncodedPose[InitialIndex],
			EncodedPose[InitialIndex + 1],
			EncodedPose[InitialIndex + 2],
			EncodedPose[InitialIndex + 3]);
		LimbRootPosition = RotationOffset.RotateVector(RootOffset);
		idx = InitialIndex + 4;
	}

	FVector LimbEffectorPosition = MayaToUnrealFVector(EncodedPose[idx], EncodedPose[idx + 1], EncodedPose[idx + 2]);
	FVector LimbDirection = MayaToUnrealFVector(EncodedPose[idx + 3], EncodedPose[idx + 4], EncodedPose[idx + 5]);
	FQuat LimbEffectorOrientation(EncodedPose[idx + 6], EncodedPose[idx + 8], EncodedPose[idx + 7], -EncodedPose[idx + 9]);

	OutRootPosition = ParentTransform.TransformPosition(LimbRootPosition);
	LimbEffectorPosition *= LimbSize;
	LimbEffectorPosition += OutRootPosition;
	OutLimbDirection = LimbDirection + OutRootPosition;
	FTransform EffectorTransform(LimbEffectorOrientation, LimbEffectorPosition, FVector(1.0, 1.0, 1.0));
	OutEffectorTransform = EffectorTransform;

}

void UIKRigDecoder::DefineSkeletonProportions(
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
)
{
	HipsHeight = InHipsHeight;
	SpineLength = InSpineLength;
	NeckLength = InNeckLength;
	LeftLegLength = InLeftLegLength;
	RightLegLength = InRightLegLength;
	LeftArmLength = InLeftArmLength;
	RightArmLength = InRightArmLength;
	NeckRootOffset = InNeckRootOffset;
	LeftLegRootOffset = InLeftLegRootOffset;
	RightLegRootOffset = InRightLegRootOffset;
	LeftArmRootOffset = InLeftArmRootOffset;
	RightArmRootOffset = InRightArmRootOffset;
}

void UIKRigDecoder::DecodePose(const TArray<float> EncodedPoseInput)
{
	int InputSize = EncodedPoseInput.Num();
	if (InputSize != 86) {
		UE_LOG(LogTemp, Log, TEXT("IKRig Decoder: Improper input size (%i)."), InputSize);
	}

	EncodedPose = EncodedPoseInput;

	GlobalTransform = FTransform(FQuat(FRotator(0.0, EncodedPose[2] * -57.2958, 0.0)),
		FVector(EncodedPose[0] * HipsHeight, EncodedPose[1] * HipsHeight, 0.0),
		FVector(1.0, 1.0, 1.0));

	DecodeLimb(SpineRootPosition, SpineDirectionVector, SpineEffectorTransform,
		EncodedPose, 3, true,
		FTransform(FVector(.0, .0, HipsHeight)), FVector(), HipsHeight, SpineLength);

	DecodeLimb(NeckRootPosition, NeckDirectionVector, NeckEffectorTransform,
		EncodedPose, 16, false,
		SpineEffectorTransform, NeckRootOffset, HipsHeight, NeckLength);

	DecodeLimb(LeftLegRootPosition, LeftLegDirectionVector, LeftLegEffectorTransform,
		EncodedPose, 30, false,
		FTransform(SpineRootPosition), LeftLegRootOffset, HipsHeight, LeftLegLength);

	DecodeLimb(RightLegRootPosition, RightLegDirectionVector, RightLegEffectorTransform,
		EncodedPose, 44, false,
		FTransform(SpineRootPosition), RightLegRootOffset, HipsHeight, RightLegLength);

	DecodeLimb(LeftArmRootPosition, LeftArmDirectionVector, LeftArmEffectorTransform,
		EncodedPose, 58, false,
		SpineEffectorTransform, LeftArmRootOffset, HipsHeight, LeftArmLength);

	DecodeLimb(RightArmRootPosition, RightArmDirectionVector, RightArmEffectorTransform,
		EncodedPose, 72, false,
		SpineEffectorTransform, RightArmRootOffset, HipsHeight, RightArmLength);
}

TArray<FVector> UIKRigDecoder::GetLimbRootPositions()
{
	TArray<FVector> OutPositionArray;
	OutPositionArray.Push(SpineRootPosition);
	OutPositionArray.Push(NeckRootPosition);
	OutPositionArray.Push(LeftLegRootPosition);
	OutPositionArray.Push(RightLegRootPosition);
	OutPositionArray.Push(LeftArmRootPosition);
	OutPositionArray.Push(RightArmRootPosition);
	return OutPositionArray;
}

TArray<FVector> UIKRigDecoder::GetLimbDirectionVectors()
{
	TArray<FVector> OutDirectionArray;
	OutDirectionArray.Push(SpineDirectionVector);
	OutDirectionArray.Push(NeckDirectionVector);
	OutDirectionArray.Push(LeftLegDirectionVector);
	OutDirectionArray.Push(RightLegDirectionVector);
	OutDirectionArray.Push(LeftArmDirectionVector);
	OutDirectionArray.Push(RightArmDirectionVector);
	return OutDirectionArray;
}

TArray<FTransform> UIKRigDecoder::GetLimbEffectorTransforms()
{
	TArray<FTransform> OutTransformArray;
	OutTransformArray.Push(SpineEffectorTransform);
	OutTransformArray.Push(NeckEffectorTransform);
	OutTransformArray.Push(LeftLegEffectorTransform);
	OutTransformArray.Push(RightLegEffectorTransform);
	OutTransformArray.Push(LeftArmEffectorTransform);
	OutTransformArray.Push(RightArmEffectorTransform);
	OutTransformArray.Push(GlobalTransform);
	return OutTransformArray;
}
