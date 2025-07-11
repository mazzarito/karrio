import React from 'react';
import { SubscriptionType } from '@karrio/types';

export const Subscription = React.createContext<{ subscription?: SubscriptionType }>({});

export const SubscriptionProvider = ({ children, subscription }: { children: React.ReactNode, subscription?: SubscriptionType }): JSX.Element => {
  return (
    <Subscription.Provider value={{ subscription }}>
      {children}
    </Subscription.Provider>
  );
};

export function useSubscription() {
  return React.useContext(Subscription);
}
