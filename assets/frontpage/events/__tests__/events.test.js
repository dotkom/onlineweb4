import React from 'react';
import { mount } from 'enzyme';
import SmallEvent from '../components/SmallEvent';


describe('<SmallEvent />', () => {
  const testUrl = 'thisIsUrl';
  const testDate = '2013-02-08';
  const wrapper = mount(<SmallEvent eventUrl={testUrl} startDate={testDate} title="event" />);

  it('renders a small event with a href to the the correct url', () => {
    expect(wrapper.find({ href: testUrl })).toBeDefined();
  });
});
