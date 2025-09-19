import React from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { useTranslation } from 'react-i18next';
import Svg, { Circle, Text as SvgText } from 'react-native-svg';

interface TrustMeterProps {
  score: number;
  size?: number;
  showLabel?: boolean;
  animated?: boolean;
}

export default function TrustMeter({ 
  score, 
  size = 80, 
  showLabel = true, 
  animated = true 
}: TrustMeterProps) {
  const { t } = useTranslation();
  const animatedValue = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    if (animated) {
      Animated.timing(animatedValue, {
        toValue: score,
        duration: 1000,
        useNativeDriver: false,
      }).start();
    } else {
      animatedValue.setValue(score);
    }
  }, [score, animated, animatedValue]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#4CAF50';
    if (score >= 60) return '#FF9800';
    return '#F44336';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return t('checkResult.confidenceLevels.high');
    if (score >= 60) return t('checkResult.confidenceLevels.medium');
    return t('checkResult.confidenceLevels.low');
  };

  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <View style={styles.container}>
      <View style={[styles.meterContainer, { width: size, height: size }]}>
        <Svg width={size} height={size} style={styles.svg}>
          {/* Background Circle */}
          <Circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e9ecef"
            strokeWidth="4"
            fill="none"
          />
          
          {/* Progress Circle */}
          <Circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={getScoreColor(score)}
            strokeWidth="4"
            fill="none"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
          />
          
          {/* Score Text */}
          <SvgText
            x={size / 2}
            y={size / 2 + 6}
            fontSize="20"
            fontWeight="bold"
            fill={getScoreColor(score)}
            textAnchor="middle"
          >
            {Math.round(score)}%
          </SvgText>
        </Svg>
      </View>
      
      {showLabel && (
        <View style={styles.labelContainer}>
          <Text style={styles.scoreLabel}>{t('checkResult.trustScore')}</Text>
          <Text style={[styles.confidenceLabel, { color: getScoreColor(score) }]}>
            {getScoreLabel(score)}
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
  },
  meterContainer: {
    position: 'relative',
  },
  svg: {
    position: 'absolute',
  },
  labelContainer: {
    marginTop: 12,
    alignItems: 'center',
  },
  scoreLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  confidenceLabel: {
    fontSize: 12,
    fontWeight: '500',
    textTransform: 'uppercase',
  },
});