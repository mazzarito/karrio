import { Address, Shipment } from '@purplship/purplship';
import React, { FormEvent, useReducer, useRef, useState } from 'react';
import { NotificationType, state } from '@/library/api';
import { deepEqual } from '@/library/helper';
import InputField from '@/components/generic/input-field';
import ButtonField from '@/components/generic/button-field';
import CheckBoxField from '@/components/generic/checkbox-field';
import CountryInput from '@/components/generic/country-input';
import StateInput from '@/components/generic/state-input';
import PostalInput from '@/components/generic/postal-input';
import PhoneInput from '@/components/generic/phone-input';

const DEFAULT_ADDRESS_CONTENT = {
    residential: false,
    country_code: Address.CountryCodeEnum.CA,
} as Partial<Address>;

interface ShipmentAddressComponent {
    shipment: Shipment;
    addressName: "shipper" | "recipient";
    update: (payload: {}, refresh?: boolean) => void;
}

function reducer(state: any, { name, value }: { name: string, value: string | boolean }) {
    return { ...state, [name]: value }
}


const ShipmentAddress: React.FC<ShipmentAddressComponent> = ({ shipment, addressName, update }) => {
    const [address, dispatch] = useReducer(reducer, shipment[addressName], () => (shipment[addressName] || DEFAULT_ADDRESS_CONTENT));
    const form = useRef<HTMLFormElement>(null);
    const [key, setKey] = useState<string>(`address-${Date.now()}`);
    const nextTab: string = { "shipper": "recipient", "recipient": "parcel" }[addressName];
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name: string = target.name;

        dispatch({ name, value });
    };
    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        try {
            if (address.id !== undefined && shipment.id !== undefined) {
                await state.updateAddress(address);
                const updated_shipment = await state.retrieveShipment(shipment.id);
                state.setNotification({ type: NotificationType.success, message: addressName + ' Address successfully updated!' });
                update({ ...updated_shipment }, true);
            } else {
                update({ [addressName]: address });
                form.current?.dispatchEvent(new CustomEvent('label-select-tab', { bubbles: true, detail: { nextTab } }));
            }
            setKey(`address-${Date.now()}`);
        } catch (err) {
            state.setNotification({ type: NotificationType.error, message: err });
        }
    };

    return (
        <form className="px-1 py-2" onSubmit={handleSubmit} key={key} ref={form}>

            <div className="columns mb-0">
                <InputField label="name" name="person_name" onChange={handleChange} defaultValue={address.person_name} fieldClass="column mb-0 px-2 py-2" required />

                <InputField label="company" name="company_name" onChange={handleChange} defaultValue={address.company_name} fieldClass="column mb-0 px-2 py-2" required={addressName === 'shipper'} />
            </div>

            <div className="columns mb-0">
                <InputField label="email" name="email" onChange={handleChange} defaultValue={address.email} fieldClass="column mb-0 px-2 py-2" type="email" />

                <PhoneInput label="phone" onValueChange={value => dispatch({ name: "phone_number", value: value as string })} defaultValue={address.phone_number} country={address.country_code} fieldClass="column mb-0 px-2 py-2" required={addressName === 'shipper'} />
            </div>


            <h6 className="is-size-7 my-2 has-text-weight-semibold">Address</h6>


            <div className="columns mb-0">
                <InputField label="Street (Line 1)" name="address_line1" onChange={handleChange} defaultValue={address.address_line1} fieldClass="column mb-0 px-2 py-2" required />

                <InputField label="Street (Line 2)" name="address_line2" onChange={handleChange} defaultValue={address.address_line2} fieldClass="column mb-0 px-2 py-2" />
            </div>

            <div className="columns is-multiline mb-0">
                <InputField label="city" name="city" onChange={handleChange} defaultValue={address.city} fieldClass="column is-6 mb-0 px-2 py-2" />

                <StateInput label="province or state" onValueChange={value => dispatch({ name: "state_code", value: value as string })} defaultValue={address.state_code} fieldClass="column is-6 mb-0 px-2 py-2" />

                <CountryInput label="country" onValueChange={value => dispatch({ name: "country_code", value: value as string })} defaultValue={address.country_code} fieldClass="column is-6 mb-0 px-2 py-2" />

                <PostalInput label="postal code" onValueChange={value => dispatch({ name: "postal_code", value: value as string })} defaultValue={address.postal_code} country={address.country_code} fieldClass="column is-6 mb-0 px-2 py-2" />
            </div>

            <div className="columns mb-0">

                <CheckBoxField name="residential" onChange={handleChange} defaultChecked={address.residential} fieldClass="column mb-0 is-12 px-2 py-2">
                    <span>Residential address</span>
                </CheckBoxField>

            </div>

            <ButtonField type="submit" className="is-primary" fieldClass="has-text-centered mt-3" disabled={deepEqual(shipment[addressName], address)}>
                <span>{address.id === undefined ? 'Continue' : 'Save'}</span>
                {address.id === undefined && <span className="icon is-small">
                    <i className="fas fa-chevron-right"></i>
                </span>}
            </ButtonField>

        </form>
    )
};

export default ShipmentAddress;